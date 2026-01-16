import { useRouter } from 'next/router'
import Head from 'next/head'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Download, Heart, Eye, Calendar, User, Tag, FileText, Share2, AlertTriangle } from 'lucide-react'
import { useQuery } from 'react-query'
import axios from 'axios'
import Layout from '@/components/Layout'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function SchematicDetail() {
  const router = useRouter()
  const { id } = router.query

  const { data: schematic, isLoading } = useQuery(
    ['schematic', id],
    async () => {
      const response = await axios.get(`${API_URL}/api/schematics/${id}/`)
      return response.data
    },
    {
      enabled: !!id,
    }
  )

  const handleDownload = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/schematics/${id}/download/`)
      window.open(response.data.download_url, '_blank')
    } catch (error) {
      console.error('Download error:', error)
      alert('Failed to download schematic')
    }
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-96 bg-secondary-200 rounded-lg mb-8" />
            <div className="h-8 bg-secondary-200 rounded w-2/3 mb-4" />
            <div className="h-4 bg-secondary-200 rounded w-1/2 mb-8" />
            <div className="h-32 bg-secondary-200 rounded" />
          </div>
        </div>
      </Layout>
    )
  }

  if (!schematic) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 py-8 text-center">
          <h1 className="text-4xl font-bold mb-4">Schematic Not Found</h1>
          <p className="text-secondary-600 mb-8">
            The schematic you're looking for doesn't exist or has been removed.
          </p>
          <Link href="/browse" className="btn-primary inline-block">
            Browse Schematics
          </Link>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <Head>
        <title>{schematic.title} - SchematicShop</title>
        <meta name="description" content={schematic.description} />
      </Head>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Thumbnail */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card overflow-hidden mb-6"
            >
              <div className="relative h-96 bg-gradient-to-br from-primary-100 to-secondary-100">
                {schematic.thumbnail_url ? (
                  <img 
                    src={schematic.thumbnail_url} 
                    alt={schematic.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="text-9xl font-bold text-secondary-300">
                      {schematic.title.charAt(0).toUpperCase()}
                    </div>
                  </div>
                )}
                
                {/* Status Badge */}
                {schematic.scan_status === 'clean' && (
                  <div className="absolute top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-full">
                    ✓ Verified Safe
                  </div>
                )}
                {schematic.scan_status === 'pending' && (
                  <div className="absolute top-4 right-4 bg-yellow-500 text-white px-4 py-2 rounded-full">
                    ⏳ Scanning...
                  </div>
                )}
              </div>
            </motion.div>

            {/* Title and Description */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card p-6 mb-6"
            >
              <h1 className="text-4xl font-bold mb-4">{schematic.title}</h1>
              
              {/* Owner Info */}
              <div className="flex items-center gap-4 text-secondary-600 mb-6 pb-6 border-b">
                <div className="flex items-center gap-2">
                  <User size={18} />
                  <span>by <span className="font-medium text-secondary-700">{schematic.owner?.username || 'Unknown'}</span></span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar size={18} />
                  <span>{new Date(schematic.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              {/* Description */}
              <div className="prose max-w-none">
                <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                  <FileText size={20} />
                  Description
                </h3>
                <p className="text-secondary-700 whitespace-pre-wrap">
                  {schematic.description || 'No description provided.'}
                </p>
              </div>
            </motion.div>

            {/* Tags */}
            {schematic.tags && schematic.tags.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="card p-6 mb-6"
              >
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Tag size={20} />
                  Tags
                </h3>
                <div className="flex gap-2 flex-wrap">
                  {schematic.tags.map((tag: any) => (
                    <Link
                      key={tag.id}
                      href={`/browse?tag=${tag.name}`}
                      className="bg-primary-100 text-primary-700 px-4 py-2 rounded-full hover:bg-primary-200 transition-colors"
                    >
                      {tag.name}
                    </Link>
                  ))}
                </div>
              </motion.div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Download Card */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="card p-6 mb-6 sticky top-24"
            >
              <button
                onClick={handleDownload}
                className="btn-primary w-full flex items-center justify-center gap-2 mb-4"
              >
                <Download size={20} />
                Download
              </button>
              
              <button className="btn-secondary w-full flex items-center justify-center gap-2 mb-6">
                <Share2 size={20} />
                Share
              </button>

              {/* Stats */}
              <div className="space-y-4 pt-6 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-secondary-600 flex items-center gap-2">
                    <Download size={18} />
                    Downloads
                  </span>
                  <span className="font-bold text-lg">{schematic.download_count || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-secondary-600 flex items-center gap-2">
                    <Heart size={18} />
                    Likes
                  </span>
                  <span className="font-bold text-lg">{schematic.likes_count || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-secondary-600 flex items-center gap-2">
                    <Eye size={18} />
                    Views
                  </span>
                  <span className="font-bold text-lg">{schematic.view_count || 0}</span>
                </div>
              </div>

              {/* File Info */}
              <div className="space-y-3 pt-6 border-t mt-6">
                <h4 className="font-semibold mb-3">File Information</h4>
                <div className="text-sm">
                  <div className="flex justify-between mb-2">
                    <span className="text-secondary-600">Size:</span>
                    <span className="font-medium">
                      {schematic.file_size ? `${(schematic.file_size / 1024 / 1024).toFixed(2)} MB` : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between mb-2">
                    <span className="text-secondary-600">Category:</span>
                    <span className="font-medium capitalize">{schematic.category || 'Other'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-secondary-600">Visibility:</span>
                    <span className="font-medium">{schematic.is_public ? 'Public' : 'Private'}</span>
                  </div>
                </div>
              </div>

              {/* Warning for pending scan */}
              {schematic.scan_status === 'pending' && (
                <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-start gap-2 text-yellow-800">
                    <AlertTriangle size={18} className="mt-0.5 flex-shrink-0" />
                    <div className="text-sm">
                      <p className="font-medium mb-1">Scan Pending</p>
                      <p className="text-yellow-700">
                        This file is being scanned for security. Download will be available once complete.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
