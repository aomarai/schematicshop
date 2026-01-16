import Head from 'next/head'
import { motion } from 'framer-motion'
import { Code, ExternalLink } from 'lucide-react'
import Layout from '@/components/Layout'

export default function Api() {
  return (
    <Layout>
      <Head>
        <title>API Documentation - SchematicShop</title>
        <meta name="description" content="SchematicShop API documentation for developers" />
      </Head>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <Code className="w-16 h-16 text-primary-600 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-4">
            <span className="gradient-text">API Documentation</span>
          </h1>
          <p className="text-secondary-600 text-lg">
            Integrate SchematicShop into your applications
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card p-8 mb-8"
        >
          <h2 className="text-2xl font-bold mb-4">Base URL</h2>
          <div className="bg-secondary-100 p-4 rounded-lg font-mono text-sm mb-6">
            https://api.schematicshop.com/api/
          </div>

          <h2 className="text-2xl font-bold mb-4 mt-8">Available Endpoints</h2>
          <div className="space-y-4">
            <div className="border-l-4 border-primary-500 pl-4">
              <code className="text-sm bg-secondary-100 px-2 py-1 rounded">GET /schematics/</code>
              <p className="text-secondary-700 mt-2">List all public schematics</p>
            </div>
            <div className="border-l-4 border-primary-500 pl-4">
              <code className="text-sm bg-secondary-100 px-2 py-1 rounded">GET /schematics/:id/</code>
              <p className="text-secondary-700 mt-2">Get schematic details</p>
            </div>
            <div className="border-l-4 border-primary-500 pl-4">
              <code className="text-sm bg-secondary-100 px-2 py-1 rounded">POST /schematics/</code>
              <p className="text-secondary-700 mt-2">Upload a new schematic (requires authentication)</p>
            </div>
            <div className="border-l-4 border-primary-500 pl-4">
              <code className="text-sm bg-secondary-100 px-2 py-1 rounded">GET /schematics/trending/</code>
              <p className="text-secondary-700 mt-2">Get trending schematics</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card p-8"
        >
          <h2 className="text-2xl font-bold mb-4">OpenAPI Documentation</h2>
          <p className="text-secondary-700 mb-6">
            For complete API documentation with interactive examples, visit our Swagger UI.
          </p>
          <a
            href="/api/docs/"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary inline-flex items-center gap-2"
          >
            View Full API Docs
            <ExternalLink size={18} />
          </a>
        </motion.div>
      </div>
    </Layout>
  )
}
