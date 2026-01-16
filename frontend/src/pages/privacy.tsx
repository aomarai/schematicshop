import Head from 'next/head'
import { motion } from 'framer-motion'
import Layout from '@/components/Layout'

export default function Privacy() {
  return (
    <Layout>
      <Head>
        <title>Privacy Policy - SchematicShop</title>
        <meta name="description" content="SchematicShop privacy policy" />
      </Head>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-4xl font-bold mb-4">Privacy Policy</h1>
          <p className="text-secondary-600 mb-8">Last updated: January 2024</p>

          <div className="prose max-w-none space-y-6">
            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Information We Collect</h2>
              <p className="text-secondary-700 mb-3">
                We collect information you provide directly to us, including:
              </p>
              <ul className="list-disc pl-6 text-secondary-700 space-y-2">
                <li>Account information (username, email, password)</li>
                <li>Schematic files and related metadata</li>
                <li>Usage data and analytics</li>
                <li>Communications with our support team</li>
              </ul>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">How We Use Your Information</h2>
              <p className="text-secondary-700 mb-3">
                We use the information we collect to:
              </p>
              <ul className="list-disc pl-6 text-secondary-700 space-y-2">
                <li>Provide and maintain our services</li>
                <li>Process your uploads and downloads</li>
                <li>Improve and optimize our platform</li>
                <li>Communicate with you about service updates</li>
                <li>Ensure security and prevent fraud</li>
              </ul>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Data Security</h2>
              <p className="text-secondary-700">
                We implement appropriate security measures to protect your personal information. All files are scanned for malware, 
                and we use encryption for data transmission and storage.
              </p>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Cookies and Tracking</h2>
              <p className="text-secondary-700">
                We use cookies and similar tracking technologies to track activity on our service and hold certain information. 
                You can instruct your browser to refuse all cookies or indicate when a cookie is being sent.
              </p>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Your Rights</h2>
              <p className="text-secondary-700 mb-3">
                You have the right to:
              </p>
              <ul className="list-disc pl-6 text-secondary-700 space-y-2">
                <li>Access and update your personal information</li>
                <li>Delete your account and associated data</li>
                <li>Export your data</li>
                <li>Opt-out of marketing communications</li>
              </ul>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Contact Us</h2>
              <p className="text-secondary-700">
                If you have any questions about this Privacy Policy, please contact us at privacy@schematicshop.com
              </p>
            </section>
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}
