import { motion } from 'framer-motion'
import { Download, Heart, Eye, Calendar } from 'lucide-react'
import { useQuery } from 'react-query'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function SchematicGrid() {
  const { data, isLoading } = useQuery('schematics', async () => {
    const response = await axios.get(`${API_URL}/api/schematics/`)
    return response.data.results || []
  })

  if (isLoading) {
    return (
      <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-48 bg-secondary-200" />
            <div className="p-4 space-y-3">
              <div className="h-4 bg-secondary-200 rounded" />
              <div className="h-3 bg-secondary-200 rounded w-2/3" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-6">
      {data?.map((schematic: any, i: number) => (
        <motion.div
          key={schematic.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          className="card group hover:shadow-glow transition-all cursor-pointer"
        >
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
                by <span className="font-medium">{schematic.owner.username}</span>
              </span>
              <span className="text-xs text-secondary-400">
                {new Date(schematic.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  )
}
