import { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Search, Filter, Download, Heart, Eye, SlidersHorizontal } from 'lucide-react'
import { useQuery } from 'react-query'
import axios from 'axios'
import Layout from '@/components/Layout'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Browse() {
  const [searchQuery, setSearchQuery] = useState('')
  const [category, setCategory] = useState('')
  const [sortBy, setSortBy] = useState('-created_at')
  const [showFilters, setShowFilters] = useState(false)

  const { data, isLoading } = useQuery(
    ['schematics', searchQuery, category, sortBy],
    async () => {
      const params = new URLSearchParams()
      if (searchQuery) params.append('search', searchQuery)
      if (category) params.append('category', category)
      params.append('ordering', sortBy)
      
      const response = await axios.get(`${API_URL}/api/schematics/?${params.toString()}`)
      return response.data.results || []
    },
    {
      enabled: true,
      staleTime: 30000,
    }
  )

  const categories = [
    { value: '', label: 'All Categories' },
    { value: 'building', label: 'Buildings' },
    { value: 'redstone', label: 'Redstone' },
    { value: 'decoration', label: 'Decoration' },
    { value: 'farm', label: 'Farms' },
    { value: 'other', label: 'Other' },
  ]

  const sortOptions = [
    { value: '-created_at', label: 'Newest First' },
    { value: 'created_at', label: 'Oldest First' },
    { value: '-download_count', label: 'Most Downloaded' },
    { value: '-view_count', label: 'Most Viewed' },
  ]

  return (
    <Layout>
      <Head>
        <title>Browse Schematics - SchematicShop</title>
        <meta name="description" content="Browse and search Minecraft schematics" />
      </Head>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">
            Browse <span className="gradient-text">Schematics</span>
          </h1>
          <p className="text-secondary-600 text-lg">
            Discover amazing Minecraft builds from the community
          </p>
        </div>

        {/* Search and Filter Bar */}
        <div className="mb-8 space-y-4">
          <div className="flex gap-4 flex-col md:flex-row">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-secondary-400" size={20} />
              <input
                type="text"
                placeholder="Search schematics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Filter Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn-secondary flex items-center gap-2 whitespace-nowrap"
            >
              <SlidersHorizontal size={18} />
              Filters
            </button>
          </div>

          {/* Filters Panel */}
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="card p-4"
            >
              <div className="grid md:grid-cols-2 gap-4">
                {/* Category Filter */}
                <div>
                  <label className="block text-sm font-medium mb-2">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    {categories.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Sort By */}
                <div>
                  <label className="block text-sm font-medium mb-2">Sort By</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    {sortOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Results Count */}
        {!isLoading && data && (
          <div className="mb-4 text-secondary-600">
            Found {data.length} schematic{data.length !== 1 ? 's' : ''}
          </div>
        )}

        {/* Schematics Grid */}
        {isLoading ? (
          <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-6">
            {[...Array(12)].map((_, i) => (
              <div key={i} className="card animate-pulse">
                <div className="h-48 bg-secondary-200" />
                <div className="p-4 space-y-3">
                  <div className="h-4 bg-secondary-200 rounded" />
                  <div className="h-3 bg-secondary-200 rounded w-2/3" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-6">
            {data?.map((schematic: any, i: number) => (
              <motion.div
                key={schematic.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.02 }}
              >
                <Link href={`/schematic/${schematic.id}`} className="block">
                  <div className="card group hover:shadow-glow transition-all cursor-pointer">
                    {/* Thumbnail */}
                    <div className="relative h-48 bg-gradient-to-br from-primary-100 to-secondary-100 overflow-hidden">
                      {schematic.thumbnail_url ? (
                        <img 
                          src={schematic.thumbnail_url} 
                          alt={schematic.title}
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <div className="text-4xl font-bold text-secondary-300">
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
                    <div className="p-4">
                      <h3 className="font-bold text-lg mb-1 truncate">{schematic.title}</h3>
                      <p className="text-sm text-secondary-600 mb-3 line-clamp-2">
                        {schematic.description || 'No description provided'}
                      </p>
                      
                      {/* Tags */}
                      {schematic.tags && schematic.tags.length > 0 && (
                        <div className="flex gap-2 mb-3 flex-wrap">
                          {schematic.tags.slice(0, 2).map((tag: any) => (
                            <span 
                              key={tag.id}
                              className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded"
                            >
                              {tag.name}
                            </span>
                          ))}
                        </div>
                      )}
                      
                      {/* Stats */}
                      <div className="flex items-center justify-between text-sm text-secondary-500">
                        <div className="flex items-center gap-3">
                          <span className="flex items-center gap-1">
                            <Download size={14} />
                            {schematic.download_count || 0}
                          </span>
                          <span className="flex items-center gap-1">
                            <Heart size={14} />
                            {schematic.likes_count || 0}
                          </span>
                          <span className="flex items-center gap-1">
                            <Eye size={14} />
                            {schematic.view_count || 0}
                          </span>
                        </div>
                      </div>
                      
                      {/* Owner */}
                      <div className="mt-3 pt-3 border-t flex items-center justify-between">
                        <span className="text-xs text-secondary-500">
                          by <span className="font-medium">{schematic.owner?.username || 'Unknown'}</span>
                        </span>
                        <span className="text-xs text-secondary-400">
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
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-2xl font-bold mb-2">No schematics found</h3>
            <p className="text-secondary-600 mb-4">
              Try adjusting your search or filters
            </p>
            <button
              onClick={() => {
                setSearchQuery('')
                setCategory('')
                setSortBy('-created_at')
              }}
              className="btn-secondary"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>
    </Layout>
  )
}
