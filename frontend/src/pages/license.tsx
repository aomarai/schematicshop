import Head from 'next/head'
import { motion } from 'framer-motion'
import Layout from '@/components/Layout'

export default function License() {
  return (
    <Layout>
      <Head>
        <title>License - SchematicShop</title>
        <meta name="description" content="SchematicShop license information" />
      </Head>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-4xl font-bold mb-4">License</h1>
          <p className="text-secondary-600 mb-8">Open Source License Information</p>

          <div className="prose max-w-none space-y-6">
            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">MIT License</h2>
              <p className="text-secondary-700 mb-4">
                SchematicShop is open source software licensed under the MIT License.
              </p>
              <div className="bg-secondary-100 p-4 rounded-lg font-mono text-sm text-secondary-800">
                <pre className="whitespace-pre-wrap">
{`MIT License

Copyright (c) 2024 SchematicShop

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.`}
                </pre>
              </div>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">User Content License</h2>
              <p className="text-secondary-700">
                By uploading content to SchematicShop, you grant us a non-exclusive, worldwide, royalty-free license to host, 
                display, and distribute your content. You retain all ownership rights to your content.
              </p>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Third-Party Licenses</h2>
              <p className="text-secondary-700 mb-3">
                SchematicShop uses various open-source libraries and tools. Key dependencies include:
              </p>
              <ul className="list-disc pl-6 text-secondary-700 space-y-2">
                <li>Next.js - MIT License</li>
                <li>React - MIT License</li>
                <li>Django - BSD License</li>
                <li>PostgreSQL - PostgreSQL License</li>
                <li>And many other open-source projects we're grateful for</li>
              </ul>
            </section>

            <section className="card p-6">
              <h2 className="text-2xl font-bold mb-4">Source Code</h2>
              <p className="text-secondary-700">
                The complete source code for SchematicShop is available on GitHub at{' '}
                <a href="https://github.com/aomarai/schematicshop" className="text-primary-600 hover:underline">
                  github.com/aomarai/schematicshop
                </a>
              </p>
            </section>
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}
