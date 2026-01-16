import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronLeft, ChevronRight, X } from 'lucide-react'

interface ImageGalleryProps {
  images: Array<{
    id: string
    image_url: string
    caption?: string
  }>
  schematicTitle?: string
}

export default function ImageGallery({ images, schematicTitle }: ImageGalleryProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)

  if (!images || images.length === 0) {
    return null
  }

  const openLightbox = (index: number) => {
    setSelectedIndex(index)
  }

  const closeLightbox = () => {
    setSelectedIndex(null)
  }

  const goToPrevious = () => {
    if (selectedIndex !== null) {
      setSelectedIndex((selectedIndex - 1 + images.length) % images.length)
    }
  }

  const goToNext = () => {
    if (selectedIndex !== null) {
      setSelectedIndex((selectedIndex + 1) % images.length)
    }
  }

  // Keyboard navigation
  useEffect(() => {
    if (selectedIndex === null) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        closeLightbox()
      } else if (e.key === 'ArrowLeft') {
        goToPrevious()
      } else if (e.key === 'ArrowRight') {
        goToNext()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [selectedIndex, images.length])

  return (
    <>
      {/* Gallery Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {images.map((image, index) => (
          <motion.div
            key={image.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            className="relative cursor-pointer group overflow-hidden rounded-lg aspect-video bg-secondary-100"
            onClick={() => openLightbox(index)}
          >
            <img
              src={image.image_url}
              alt={image.caption || (schematicTitle ? `Build image ${index + 1} for ${schematicTitle}` : `Gallery image ${index + 1}`)}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
            />
            {image.caption && (
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-3">
                <p className="text-white text-sm truncate">{image.caption}</p>
              </div>
            )}
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all" />
          </motion.div>
        ))}
      </div>

      {/* Lightbox */}
      <AnimatePresence>
        {selectedIndex !== null && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            role="dialog"
            aria-modal="true"
            aria-label="Image gallery lightbox"
            className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center p-4"
            onClick={closeLightbox}
          >
            {/* Close Button */}
            <button
              onClick={closeLightbox}
              aria-label="Close lightbox"
              className="absolute top-4 right-4 text-white hover:text-secondary-300 transition-colors z-10"
            >
              <X size={32} />
            </button>

            {/* Previous Button */}
            {images.length > 1 && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  goToPrevious()
                }}
                aria-label="Previous image"
                className="absolute left-4 text-white hover:text-secondary-300 transition-colors z-10"
              >
                <ChevronLeft size={48} />
              </button>
            )}

            {/* Image */}
            <motion.div
              key={selectedIndex}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="max-w-7xl max-h-full"
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={images[selectedIndex].image_url}
                alt={images[selectedIndex].caption || (schematicTitle ? `Build image ${selectedIndex + 1} for ${schematicTitle}` : `Gallery image ${selectedIndex + 1}`)}
                className="max-w-full max-h-[85vh] object-contain rounded-lg"
              />
              {images[selectedIndex].caption && (
                <div className="text-center mt-4">
                  <p className="text-white text-lg">{images[selectedIndex].caption}</p>
                </div>
              )}
              <div className="text-center mt-2">
                <p className="text-secondary-400 text-sm">
                  {selectedIndex + 1} / {images.length}
                </p>
              </div>
            </motion.div>

            {/* Next Button */}
            {images.length > 1 && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  goToNext()
                }}
                aria-label="Next image"
                className="absolute right-4 text-white hover:text-secondary-300 transition-colors z-10"
              >
                <ChevronRight size={48} />
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
