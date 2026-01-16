import Head from 'next/head'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { TrendingUp, Download, Heart, Eye, Calendar } from 'lucide-react'
import { useQuery } from 'react-query'
import axios from 'axios'
import Layout from '@/components/Layout'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Trending() {
  const { data, isLoading } = useQuery(
    'trending-schematics',
    async () => {
      const response = await axios.get(`${API_URL}/api/schematics/trending/`)
      return response.data || []
    },
    {
      staleTime: 60000, // Cache for 1 minute
    }
  )

  return (
    <Layout>
      <Head>
        <title>Trending Schematics - SchematicShop</title>
        <meta name="description" content="Discover the most popular Minecraft schematics this week" />
      </Head>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <TrendingUp className="w-10 h-10 text-primary-600" />
            <h1 className="text-4xl font-bold">
              Trending <span className="gradient-text">This Week</span>
            </h1>
          </div>
          <p className="text-secondary-600 text-lg">
            The most popular schematics from the past 7 days
          </p>
        </div>

        {/* Trending Schematics */}
        {isLoading ? (
          <div className="space-y-6">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="card animate-pulse flex flex-col md:flex-row gap-4">
                <div className="w-full md:w-64 h-48 bg-secondary-200" />
                <div className="flex-1 p-4 space-y-3">
                  <div className="h-6 bg-secondary-200 rounded w-3/4" />
                  <div className="h-4 bg-secondary-200 rounded w-1/2" />
                  <div className="h-4 bg-secondary-200 rounded w-full" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-6">
            {data?.map((schematic: any, index: number) => (
              <motion.div
                key={schematic.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Link href={`/schematic/${schematic.id}`}>
                  <div className="card hover:shadow-glow transition-all cursor-pointer flex flex-col md:flex-row gap-4 group">
                    {/* Rank Badge */}
                    <div className="absolute top-4 left-4 md:static md:flex md:items-start md:pt-4 md:pl-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-primary-400 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
                        #{index + 1}
                      </div>
                    </div>

                    {/* Thumbnail */}
                    <div className="relative w-full md:w-64 h-48 bg-gradient-to-br from-primary-100 to-secondary-100 overflow-hidden rounded-t-lg md:rounded-l-lg md:rounded-tr-none">
                      {schematic.thumbnail_url ? (
                        <img 
                          src={schematic.thumbnail_url} 
                          alt={schematic.title}
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <div className="text-5xl font-bold text-secondary-300">
                            {schematic.title.charAt(0).toUpperCase()}
                          </div>
                        </div>
                      )}
                      
                      {/* Status Badge */}
                      {schematic.scan_status === 'clean' && (
                        <div className="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                          ✓ Verified
                        </div>
                      )}
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1 p-4">
                      <h3 className="font-bold text-2xl mb-2">{schematic.title}</h3>
                      <p className="text-secondary-600 mb-4 line-clamp-2">
                        {schematic.description || 'No description provided'}
                      </p>
                      
                      {/* Tags */}
                      {schematic.tags && schematic.tags.length > 0 && (
                        <div className="flex gap-2 mb-4 flex-wrap">
                          {schematic.tags.slice(0, 3).map((tag: any) => (
                            <span 
                              key={tag.id}
                              className="text-xs bg-primary-100 text-primary-700 px-3 py-1 rounded-full"
                            >
                              {tag.name}
                            </span>
                          ))}
                        </div>
                      )}
                      
                      {/* Stats */}
                      <div className="flex items-center gap-6 text-sm text-secondary-600 mb-3">
                        <span className="flex items-center gap-2">
                          <Download size={16} className="text-primary-600" />
                          <span className="font-medium">{schematic.download_count || 0}</span> downloads
                        </span>
                        <span className="flex items-center gap-2">
                          <Heart size={16} className="text-red-500" />
                          <span className="font-medium">{schematic.likes_count || 0}</span> likes
                        </span>
                        <span className="flex items-center gap-2">
                          <Eye size={16} className="text-blue-500" />
                          <span className="font-medium">{schematic.view_count || 0}</span> views
                        </span>
                      </div>
                      
                      {/* Owner & Date */}
                      <div className="flex items-center gap-4 text-sm text-secondary-500 pt-3 border-t">
                        <span>
                          by <span className="font-medium text-secondary-700">{schematic.owner?.username || 'Unknown'}</span>
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar size={14} />
                          {new Date(schematic.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && data && data.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-2xl font-bold mb-2">No trending schematics yet</h3>
            <p className="text-secondary-600 mb-4">
              Check back later for popular builds
            </p>
            <Link href="/browse" className="btn-primary inline-block">
              Browse All Schematics
            </Link>
          </div>
        )}
      </div>
    </Layout>
  )
}
