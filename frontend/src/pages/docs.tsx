import Head from 'next/head'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Book, Upload, Download, Search, Shield, Code } from 'lucide-react'
import Layout from '@/components/Layout'

export default function Docs() {
  const sections = [
    {
      icon: Upload,
      title: 'Getting Started',
      description: 'Learn how to upload and share your first schematic',
      items: [
        'Create an account or log in',
        'Click the "Upload" button in the header',
        'Select your .schem, .schematic, .litematic, or .nbt file',
        'Add a title, description, and tags',
        'Choose your category and visibility settings',
        'Click "Upload Schematic" to share your build'
      ]
    },
    {
      icon: Search,
      title: 'Finding Schematics',
      description: 'Discover builds that match your needs',
      items: [
        'Browse all schematics from the Browse page',
        'Use the search bar to find specific builds',
        'Filter by category, tags, and sorting options',
        'Check out trending builds for popular content',
        'View detailed information on each schematic page'
      ]
    },
    {
      icon: Download,
      title: 'Downloading',
      description: 'How to download and use schematics',
      items: [
        'Navigate to any schematic detail page',
        'Click the "Download" button',
        'All files are automatically scanned for security',
        'Use the downloaded file with Minecraft tools like WorldEdit or Litematica',
        'Give credit to the original creator when sharing builds'
      ]
    },
    {
      icon: Shield,
      title: 'Security',
      description: 'How we keep your files safe',
      items: [
        'All uploaded files are automatically scanned',
        'Files are stored securely in the cloud',
        'Only verified clean files can be downloaded',
        'Regular security audits and updates',
        'Report any suspicious content to our team'
      ]
    },
    {
      icon: Code,
      title: 'API Access',
      description: 'Integrate SchematicShop into your tools',
      items: [
        'RESTful API available for developers',
        'Browse our API documentation',
        'Authenticate with API tokens',
        'Upload, download, and search programmatically',
        'Rate limits apply to ensure fair usage'
      ]
    }
  ]

  return (
    <Layout>
      <Head>
        <title>Documentation - SchematicShop</title>
        <meta name="description" content="Learn how to use SchematicShop to share and discover Minecraft schematics" />
      </Head>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-block mb-4"
          >
            <Book className="w-16 h-16 text-primary-600 mx-auto" />
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl font-bold mb-4"
          >
            <span className="gradient-text">Documentation</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-secondary-600 text-lg max-w-2xl mx-auto"
          >
            Everything you need to know about using SchematicShop
          </motion.p>
        </div>

        {/* Documentation Sections */}
        <div className="space-y-8">
          {sections.map((section, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              className="card p-8"
            >
              <div className="flex items-start gap-4 mb-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <section.icon className="w-6 h-6 text-primary-600" />
                </div>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold mb-2">{section.title}</h2>
                  <p className="text-secondary-600">{section.description}</p>
                </div>
              </div>
              <ul className="space-y-3 ml-16">
                {section.items.map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <span className="text-primary-600 font-bold mt-1">→</span>
                    <span className="text-secondary-700">{item}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Quick Links */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-12 card p-8 bg-gradient-to-br from-primary-50 to-secondary-50"
        >
          <h2 className="text-2xl font-bold mb-6 text-center">Quick Links</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <Link href="/upload" className="btn-primary text-center">
              Start Uploading
            </Link>
            <Link href="/browse" className="btn-secondary text-center">
              Browse Schematics
            </Link>
            <Link href="/support" className="btn-secondary text-center">
              Get Support
            </Link>
          </div>
        </motion.div>

        {/* FAQ */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mt-8 card p-8"
        >
          <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-bold text-lg mb-2">What file formats are supported?</h3>
              <p className="text-secondary-700">
                We support .schem, .schematic, .litematic, and .nbt files. Maximum file size is 50MB.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">Are all schematics free?</h3>
              <p className="text-secondary-700">
                Yes! All schematics on SchematicShop are free to download and use.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">How do I use a schematic in Minecraft?</h3>
              <p className="text-secondary-700">
                You'll need mods like WorldEdit, Litematica, or similar tools to import schematics into your Minecraft world.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">Can I delete or edit my uploads?</h3>
              <p className="text-secondary-700">
                Yes, you can manage all your uploads from your profile page.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}
