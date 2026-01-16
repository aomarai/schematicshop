import Head from 'next/head'
import { motion } from 'framer-motion'
import { Mail, MessageCircle, Github } from 'lucide-react'
import Layout from '@/components/Layout'

export default function Support() {
  return (
    <Layout>
      <Head>
        <title>Support - SchematicShop</title>
        <meta name="description" content="Get help and support for SchematicShop" />
      </Head>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold mb-4">
            <span className="gradient-text">Support</span>
          </h1>
          <p className="text-secondary-600 text-lg">
            We're here to help you with any questions or issues
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card p-6 text-center"
          >
            <Mail className="w-12 h-12 text-primary-600 mx-auto mb-4" />
            <h3 className="font-bold text-lg mb-2">Email</h3>
            <p className="text-secondary-600 text-sm mb-4">
              Send us an email and we'll respond within 24 hours
            </p>
            <a href="mailto:support@schematicshop.com" className="text-primary-600 hover:underline">
              support@schematicshop.com
            </a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card p-6 text-center"
          >
            <MessageCircle className="w-12 h-12 text-primary-600 mx-auto mb-4" />
            <h3 className="font-bold text-lg mb-2">Discord</h3>
            <p className="text-secondary-600 text-sm mb-4">
              Join our community for quick help and discussions
            </p>
            <a href="#" className="text-primary-600 hover:underline">
              Join Discord
            </a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card p-6 text-center"
          >
            <Github className="w-12 h-12 text-primary-600 mx-auto mb-4" />
            <h3 className="font-bold text-lg mb-2">GitHub</h3>
            <p className="text-secondary-600 text-sm mb-4">
              Report bugs or request features on GitHub
            </p>
            <a href="https://github.com/aomarai/schematicshop" className="text-primary-600 hover:underline">
              View Repository
            </a>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card p-8"
        >
          <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-bold text-lg mb-2">How do I report a problem?</h3>
              <p className="text-secondary-700">
                You can report issues via email, Discord, or by creating an issue on our GitHub repository.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">My upload failed. What should I do?</h3>
              <p className="text-secondary-700">
                Check that your file is under 50MB and in a supported format (.schem, .schematic, .litematic, .nbt). If the problem persists, contact support.
              </p>
            </div>
            <div>
              <h3 className="font-bold text-lg mb-2">How do I delete my account?</h3>
              <p className="text-secondary-700">
                Contact support via email with your account details, and we'll process your request within 48 hours.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}
