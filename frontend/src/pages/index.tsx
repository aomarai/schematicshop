import Head from 'next/head'
import { motion } from 'framer-motion'
import { Upload, Search, Share2, Shield, Zap, Globe } from 'lucide-react'
import Layout from '@/components/Layout'
import SchematicGrid from '@/components/SchematicGrid'

export default function Home() {
  return (
    <Layout>
      <Head>
        <title>SchematicShop - Cloud-Native Minecraft Schematic Hosting</title>
        <meta name="description" content="Upload, share, and discover Minecraft schematics and litematica files" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 to-secondary-50 -z-10" />
        <div className="max-w-7xl mx-auto text-center">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-6xl font-bold mb-6"
          >
            Share Your <span className="gradient-text">Minecraft</span> Builds
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl text-secondary-600 mb-8 max-w-2xl mx-auto"
          >
            The modern, cloud-native platform for hosting and discovering Minecraft schematics and litematica files.
          </motion.p>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex gap-4 justify-center"
          >
            <button className="btn-primary text-lg px-8 py-3">
              <Upload className="inline mr-2" size={20} />
              Upload Schematic
            </button>
            <button className="btn-secondary text-lg px-8 py-3">
              <Search className="inline mr-2" size={20} />
              Browse Library
            </button>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-16">
            Built for <span className="gradient-text">Performance</span>
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Shield,
                title: 'Secure & Safe',
                description: 'Automatic virus scanning and validation for every upload'
              },
              {
                icon: Zap,
                title: 'Lightning Fast',
                description: 'CDN-powered downloads with global edge distribution'
              },
              {
                icon: Globe,
                title: 'Cloud Native',
                description: 'Scalable microservices architecture built for growth'
              },
              {
                icon: Share2,
                title: 'Easy Sharing',
                description: 'Share your builds with the community in seconds'
              },
              {
                icon: Search,
                title: 'Smart Search',
                description: 'Find exactly what you need with powerful search filters'
              },
              {
                icon: Upload,
                title: 'Simple Upload',
                description: 'Drag and drop interface with real-time progress tracking'
              }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
                className="card p-8 hover:shadow-glow transition-shadow"
              >
                <feature.icon className="w-12 h-12 text-primary-600 mb-4" />
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-secondary-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Trending Schematics */}
      <section className="py-20 px-4 bg-secondary-50">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-12">
            <h2 className="text-4xl font-bold">
              Trending <span className="gradient-text">Builds</span>
            </h2>
            <button className="btn-secondary">View All</button>
          </div>
          <SchematicGrid />
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-br from-primary-600 to-primary-700 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Share Your Builds?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of builders sharing their creations on SchematicShop
          </p>
          <button className="bg-white text-primary-600 hover:bg-primary-50 btn text-lg px-8 py-3">
            Get Started Free
          </button>
        </div>
      </section>
    </Layout>
  )
}
