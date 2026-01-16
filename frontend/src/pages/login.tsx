import { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { motion } from 'framer-motion'
import { LogIn, AlertCircle } from 'lucide-react'
import Layout from '@/components/Layout'
import SocialLoginButtons from '@/components/SocialLoginButtons'
import { useAuth } from '@/contexts/AuthContext'

export default function Login() {
  const router = useRouter()
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login(username, password)
      // Redirect to upload page or return to previous page
      const returnUrl = (router.query.returnUrl as string) || '/upload'
      router.push(returnUrl)
    } catch (err: any) {
      console.error('Login error:', err)
      setError(
        err.response?.data?.detail || 
        err.response?.data?.message ||
        'Invalid username or password'
      )
      setIsLoading(false)
    }
  }

  return (
    <Layout>
      <Head>
        <title>Login - SchematicShop</title>
        <meta name="description" content="Login to SchematicShop" />
      </Head>

      <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
              <LogIn className="w-8 h-8 text-primary-600" />
            </div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome <span className="gradient-text">Back</span>
            </h1>
            <p className="text-secondary-600">
              Login to upload and manage your schematics
            </p>
          </div>

          <div className="card p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3"
                >
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-red-800 text-sm">{error}</p>
                </motion.div>
              )}

              <div>
                <label htmlFor="username" className="block text-sm font-medium mb-2">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoComplete="username"
                  disabled={isLoading}
                  className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-secondary-100"
                  placeholder="Enter your username"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium mb-2">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  disabled={isLoading}
                  className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-secondary-100"
                  placeholder="Enter your password"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <LogIn size={18} />
                {isLoading ? 'Logging in...' : 'Login'}
              </button>
            </form>

            <div className="mt-6">
              <SocialLoginButtons mode="login" />
            </div>

            <div className="mt-6 text-center">
              <p className="text-secondary-600">
                Don't have an account?{' '}
                <Link href="/register" className="text-primary-600 hover:text-primary-700 font-medium">
                  Register here
                </Link>
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}
