import { useState, useCallback } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { motion } from 'framer-motion'
import { Upload as UploadIcon, File, X, CheckCircle, AlertCircle } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import Layout from '@/components/Layout'
import ImageUpload from '@/components/ImageUpload'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Upload() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [images, setImages] = useState<File[]>([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('building')
  const [tags, setTags] = useState('')
  const [isPublic, setIsPublic] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStage, setUploadStage] = useState<'schematic' | 'images'>('schematic')
  const [uploadError, setUploadError] = useState('')
  const [uploadSuccess, setUploadSuccess] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0]
      setFile(selectedFile)
      
      // Auto-populate title from filename if empty
      if (!title) {
        const filename = selectedFile.name.replace(/\.[^/.]+$/, '')
        setTitle(filename)
      }
    }
  }, [title])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/octet-stream': ['.schem', '.schematic', '.litematic', '.nbt']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!file) {
      setUploadError('Please select a file to upload')
      return
    }

    if (!title.trim()) {
      setUploadError('Please provide a title')
      return
    }

    setIsUploading(true)
    setUploadError('')
    setUploadProgress(0)
    setUploadStage('schematic')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', title.trim())
      formData.append('description', description.trim())
      formData.append('category', category)
      formData.append('is_public', String(isPublic))
      
      // Parse and add tags as array (backend expects tag_names as ListField)
      const tagList = tags.split(',').map(tag => tag.trim()).filter(Boolean)
      if (tagList.length > 0) {
        formData.append('tag_names', JSON.stringify(tagList))
      }

      const response = await axios.post(
        `${API_URL}/api/schematics/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              setUploadProgress(percentCompleted)
            }
          },
        }
      )

      const schematicId = response.data.id

      // Upload images if any
      if (images.length > 0) {
        setUploadStage('images')
        setUploadProgress(0)
        
        try {
          for (let i = 0; i < images.length; i++) {
            const imageFormData = new FormData()
            imageFormData.append('image', images[i])
            imageFormData.append('order', String(i))

            await axios.post(
              `${API_URL}/api/schematics/${schematicId}/upload_image/`,
              imageFormData,
              {
                headers: {
                  'Content-Type': 'multipart/form-data',
                },
                onUploadProgress: (progressEvent) => {
                  if (progressEvent.total) {
                    const imageProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                    // Show overall image upload progress
                    const totalProgress = Math.round(((i + imageProgress / 100) / images.length) * 100)
                    setUploadProgress(totalProgress)
                  }
                },
              }
            )
          }
        } catch (imageError: any) {
          console.error('Image upload error:', imageError)
          // Partial success - schematic uploaded but some images failed
          setUploadError(
            `Schematic uploaded successfully, but some images failed: ${
              imageError.response?.data?.error || 
              imageError.response?.data?.detail || 
              imageError.response?.data?.message ||
              'Image upload error'
            }`
          )
          setIsUploading(false)
          setTimeout(() => {
            router.push(`/schematic/${schematicId}`)
          }, 3000)
          return
        }
      }

      setUploadSuccess(true)
      setTimeout(() => {
        router.push(`/schematic/${schematicId}`)
      }, 2000)
    } catch (error: any) {
      console.error('Upload error:', error)
      setUploadError(
        error.response?.data?.error ||
        error.response?.data?.detail || 
        error.response?.data?.message ||
        'Failed to upload schematic. Please try again.'
      )
      setIsUploading(false)
    }
  }

  const removeFile = () => {
    setFile(null)
    setUploadProgress(0)
  }

  const categories = [
    { value: 'building', label: 'Building' },
    { value: 'redstone', label: 'Redstone' },
    { value: 'decoration', label: 'Decoration' },
    { value: 'farm', label: 'Farm' },
    { value: 'other', label: 'Other' },
  ]

  return (
    <Layout>
      <Head>
        <title>Upload Schematic - SchematicShop</title>
        <meta name="description" content="Upload your Minecraft schematic to SchematicShop" />
      </Head>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold mb-4">
            Upload <span className="gradient-text">Schematic</span>
          </h1>
          <p className="text-secondary-600 text-lg">
            Share your Minecraft builds with the community
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Upload */}
          <div className="card p-6">
            <label className="block text-sm font-medium mb-3">
              Schematic File *
            </label>
            
            {!file ? (
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
                  isDragActive 
                    ? 'border-primary-500 bg-primary-50' 
                    : 'border-secondary-300 hover:border-primary-400 hover:bg-secondary-50'
                }`}
              >
                <input {...getInputProps()} />
                <UploadIcon className="w-16 h-16 mx-auto mb-4 text-secondary-400" />
                <p className="text-lg font-medium mb-2">
                  {isDragActive ? 'Drop your file here' : 'Drag & drop your schematic file'}
                </p>
                <p className="text-sm text-secondary-500 mb-4">
                  or click to browse
                </p>
                <p className="text-xs text-secondary-400">
                  Supports: .schem, .schematic, .litematic, .nbt (max 50MB)
                </p>
              </div>
            ) : (
              <div className="flex items-center justify-between p-4 bg-secondary-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <File className="w-8 h-8 text-primary-600" />
                  <div>
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-secondary-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                {!isUploading && (
                  <button
                    type="button"
                    onClick={removeFile}
                    className="text-secondary-500 hover:text-red-600"
                  >
                    <X size={20} />
                  </button>
                )}
              </div>
            )}

            {/* Upload Progress */}
            {isUploading && (
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">
                    {uploadStage === 'schematic' ? 'Uploading schematic...' : `Uploading images (${uploadProgress}%)...`}
                  </span>
                  <span className="text-sm text-secondary-600">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-secondary-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Title */}
          <div className="card p-6">
            <label htmlFor="title" className="block text-sm font-medium mb-3">
              Title *
            </label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="My awesome build"
              required
              disabled={isUploading}
              className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-secondary-100"
            />
          </div>

          {/* Description */}
          <div className="card p-6">
            <label htmlFor="description" className="block text-sm font-medium mb-3">
              Description
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe your build..."
              rows={4}
              disabled={isUploading}
              className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-secondary-100"
            />
          </div>

          {/* Category and Tags */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="card p-6">
              <label htmlFor="category" className="block text-sm font-medium mb-3">
                Category
              </label>
              <select
                id="category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                disabled={isUploading}
                className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-secondary-100"
              >
                {categories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="card p-6">
              <label htmlFor="tags" className="block text-sm font-medium mb-3">
                Tags
              </label>
              <input
                id="tags"
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="medieval, castle, survival"
                disabled={isUploading}
                className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-secondary-100"
              />
              <p className="text-xs text-secondary-500 mt-2">
                Separate tags with commas
              </p>
            </div>
          </div>

          {/* Build Images */}
          <div className="card p-6">
            <ImageUpload 
              onImagesChange={setImages}
              maxImages={10}
            />
          </div>

          {/* Visibility */}
          <div className="card p-6">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={isPublic}
                onChange={(e) => setIsPublic(e.target.checked)}
                disabled={isUploading}
                className="w-5 h-5 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
              />
              <div>
                <div className="font-medium">Make this schematic public</div>
                <div className="text-sm text-secondary-600">
                  Public schematics can be discovered and downloaded by anyone
                </div>
              </div>
            </label>
          </div>

          {/* Error Message */}
          {uploadError && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="card p-4 bg-red-50 border border-red-200"
            >
              <div className="flex items-center gap-3 text-red-800">
                <AlertCircle size={20} />
                <p>{uploadError}</p>
              </div>
            </motion.div>
          )}

          {/* Success Message */}
          {uploadSuccess && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="card p-4 bg-green-50 border border-green-200"
            >
              <div className="flex items-center gap-3 text-green-800">
                <CheckCircle size={20} />
                <p>Upload successful! Redirecting...</p>
              </div>
            </motion.div>
          )}

          {/* Submit Button */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={isUploading || !file || uploadSuccess}
              className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <UploadIcon size={18} />
              {isUploading ? 'Uploading...' : 'Upload Schematic'}
            </button>
            <button
              type="button"
              onClick={() => router.push('/browse')}
              disabled={isUploading}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </Layout>
  )
}
