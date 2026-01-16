import { ReactNode } from 'react'
import Link from 'next/link'
import { Upload, Search, User } from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 glass border-b border-secondary-200">
        <nav className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-400 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">S</span>
            </div>
            <span className="text-xl font-bold">SchematicShop</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-6">
            <Link href="/browse" className="text-secondary-700 hover:text-primary-600 transition-colors">
              Browse
            </Link>
            <Link href="/trending" className="text-secondary-700 hover:text-primary-600 transition-colors">
              Trending
            </Link>
            <Link href="/docs" className="text-secondary-700 hover:text-primary-600 transition-colors">
              Docs
            </Link>
          </div>
          
          <div className="flex items-center gap-3">
            <button className="btn-secondary hidden md:flex items-center gap-2">
              <Search size={18} />
              Search
            </button>
            <button className="btn-primary flex items-center gap-2">
              <Upload size={18} />
              <span className="hidden md:inline">Upload</span>
            </button>
            <button className="btn-secondary">
              <User size={18} />
            </button>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-secondary-900 text-white py-12 px-4">
        <div className="max-w-7xl mx-auto grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-primary-400 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">S</span>
              </div>
              <span className="font-bold">SchematicShop</span>
            </div>
            <p className="text-secondary-400 text-sm">
              Modern platform for hosting Minecraft schematics
            </p>
          </div>
          
          <div>
            <h4 className="font-bold mb-4">Platform</h4>
            <ul className="space-y-2 text-sm text-secondary-400">
              <li><Link href="/browse" className="hover:text-white">Browse</Link></li>
              <li><Link href="/upload" className="hover:text-white">Upload</Link></li>
              <li><Link href="/trending" className="hover:text-white">Trending</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-bold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm text-secondary-400">
              <li><Link href="/docs" className="hover:text-white">Documentation</Link></li>
              <li><Link href="/api" className="hover:text-white">API</Link></li>
              <li><Link href="/support" className="hover:text-white">Support</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-bold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-secondary-400">
              <li><Link href="/privacy" className="hover:text-white">Privacy</Link></li>
              <li><Link href="/terms" className="hover:text-white">Terms</Link></li>
              <li><Link href="/license" className="hover:text-white">License</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="max-w-7xl mx-auto mt-8 pt-8 border-t border-secondary-800 text-center text-sm text-secondary-400">
          © 2024 SchematicShop. Built with Django, Next.js, and ❤️
        </div>
      </footer>
    </div>
  )
}
