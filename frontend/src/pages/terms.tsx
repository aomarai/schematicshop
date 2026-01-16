import Head from 'next/head'
import { motion } from 'framer-motion'
import Layout from '@/components/Layout'

export default function Terms() {
  return (
    <Layout>
      <Head>
        <title>Terms of Service - SchematicShop</title>
        <meta name="description" content="SchematicShop terms of service" />
      </Head>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-4xl font-bold mb-4">Terms of Service</h1>
          <p className="text-secondary-600 mb-8">Last updated: January 2024</p>

          <div className="prose max-w-none space-y-6">
            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Acceptance of Terms</h2>
              <p className="text-secondary-700">
                By accessing and using SchematicShop, you accept and agree to be bound by the terms and provisions of this agreement.
              </p>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">User Accounts</h2>
              <p className="text-secondary-700 mb-3">
                When you create an account with us, you must provide accurate, complete, and current information. You are responsible for:
              </p>
              <ul className="list-disc pl-6 text-secondary-700 space-y-2">
                <li>Maintaining the security of your account</li>
                <li>All activities that occur under your account</li>
                <li>Notifying us of any unauthorized use</li>
              </ul>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Content Guidelines</h2>
              <p className="text-secondary-700 mb-3">
                When uploading content, you agree that:
              </p>
              <ul className="list-disc pl-6 text-secondary-700 space-y-2">
                <li>You own or have rights to the content you upload</li>
                <li>Your content does not violate any third-party rights</li>
                <li>Your content does not contain malware or harmful code</li>
                <li>Your content complies with applicable laws</li>
              </ul>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Prohibited Activities</h2>
              <p className="text-secondary-700 mb-3">
                You may not:
              </p>
              <ul className="list-disc pl-6 text-secondary-700 space-y-2">
                <li>Upload malicious files or viruses</li>
                <li>Attempt to gain unauthorized access to our systems</li>
                <li>Use our service for illegal purposes</li>
                <li>Harass or harm other users</li>
                <li>Violate intellectual property rights</li>
              </ul>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Termination</h2>
              <p className="text-secondary-700">
                We reserve the right to terminate or suspend your account immediately, without prior notice, for conduct that we believe 
                violates these Terms of Service or is harmful to other users, us, or third parties.
              </p>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Disclaimer</h2>
              <p className="text-secondary-700">
                Our service is provided "as is" without warranties of any kind. We do not guarantee that the service will be uninterrupted, 
                secure, or error-free.
              </p>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Changes to Terms</h2>
              <p className="text-secondary-700">
                We reserve the right to modify these terms at any time. We will notify users of any significant changes via email or 
                through our service.
              </p>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Contact</h2>
              <p className="text-secondary-700">
                If you have questions about these Terms, contact us at legal@schematicshop.com
              </p>
            </section>
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}
