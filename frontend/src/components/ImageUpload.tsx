import { useState, useCallback, useEffect, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import { X, Image as ImageIcon } from 'lucide-react'

interface ImageUploadProps {
  onImagesChange: (images: File[]) => void
  maxImages?: number
}

interface PreviewImage {
  file: File
  preview: string
}

export default function ImageUpload({ onImagesChange, maxImages = 10 }: ImageUploadProps) {
  const [images, setImages] = useState<PreviewImage[]>([])
  const urlsRef = useRef<Set<string>>(new Set())

  // Cleanup object URLs only on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      urlsRef.current.forEach(url => URL.revokeObjectURL(url))
      urlsRef.current.clear()
    }
  }, [])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const remainingSlots = maxImages - images.length
    const filesToAdd = acceptedFiles.slice(0, remainingSlots)

    const newImages = filesToAdd.map(file => {
      const preview = URL.createObjectURL(file)
      urlsRef.current.add(preview)
      return { file, preview }
    })

    const updatedImages = [...images, ...newImages]
    setImages(updatedImages)
    onImagesChange(updatedImages.map(img => img.file))
  }, [images, maxImages, onImagesChange])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.webp']
    },
    maxFiles: maxImages,
    maxSize: 5 * 1024 * 1024, // 5MB
  })

  const removeImage = (index: number) => {
    // Revoke the URL before removing
    const url = images[index].preview
    URL.revokeObjectURL(url)
    urlsRef.current.delete(url)
    const updatedImages = images.filter((_, i) => i !== index)
    setImages(updatedImages)
    onImagesChange(updatedImages.map(img => img.file))
  }

  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium mb-3">
        Build Images (Optional)
      </label>
      
      {images.length < maxImages && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive 
              ? 'border-primary-500 bg-primary-50' 
              : 'border-secondary-300 hover:border-primary-400 hover:bg-secondary-50'
          }`}
        >
          <input {...getInputProps()} />
          <ImageIcon className="w-12 h-12 mx-auto mb-3 text-secondary-400" />
          <p className="text-sm font-medium mb-1">
            {isDragActive ? 'Drop images here' : 'Drag & drop build images'}
          </p>
          <p className="text-xs text-secondary-500 mb-2">
            or click to browse
          </p>
          <p className="text-xs text-secondary-400">
            Supports: JPG, PNG, WebP (max 5MB each, up to {maxImages} images)
          </p>
        </div>
      )}

      {images.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {images.map((image, index) => (
            <div key={index} className="relative group">
              <img
                src={image.preview}
                alt={`Preview ${index + 1}`}
                className="w-full h-32 object-cover rounded-lg border border-secondary-200"
              />
              <button
                type="button"
                onClick={() => removeImage(index)}
                className="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X size={16} />
              </button>
              <div className="absolute bottom-2 left-2 bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded">
                {index + 1} of {images.length}
              </div>
            </div>
          ))}
        </div>
      )}

      {images.length > 0 && (
        <p className="text-sm text-secondary-600">
          {images.length} image{images.length !== 1 ? 's' : ''} selected
          {images.length >= maxImages && ' (maximum reached)'}
        </p>
      )}
    </div>
  )
}
