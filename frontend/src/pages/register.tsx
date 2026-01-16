import { useState } from 'react'
import Head from 'next/head'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { motion } from 'framer-motion'
import { UserPlus, AlertCircle } from 'lucide-react'
import Layout from '@/components/Layout'
import { useAuth } from '@/contexts/AuthContext'

export default function Register() {
  const router = useRouter()
  const { register } = useAuth()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validation
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long')
      return
    }

    setIsLoading(true)

    try {
      await register(username, email, password)
      // Redirect to upload page after successful registration
      router.push('/upload')
    } catch (err: any) {
      console.error('Registration error:', err)
      const errorData = err.response?.data
      
      if (errorData) {
        // Handle field-specific errors
        if (errorData.username) {
          setError(`Username: ${errorData.username.join(', ')}`)
        } else if (errorData.email) {
          setError(`Email: ${errorData.email.join(', ')}`)
        } else if (errorData.password) {
          setError(`Password: ${errorData.password.join(', ')}`)
        } else if (errorData.detail) {
          setError(errorData.detail)
        } else {
          setError('Registration failed. Please try again.')
        }
      } else {
        setError('Registration failed. Please try again.')
      }
      setIsLoading(false)
    }
  }

  return (
    <Layout>
      <Head>
        <title>Register - SchematicShop</title>
        <meta name="description" content="Create a SchematicShop account" />
      </Head>

      <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
              <UserPlus className="w-8 h-8 text-primary-600" />
            </div>
            <h1 className="text-3xl font-bold mb-2">
              Create <span className="gradient-text">Account</span>
            </h1>
            <p className="text-secondary-600">
              Join SchematicShop to upload and share your builds
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
                  placeholder="Choose a username"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-2">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  disabled={isLoading}
                  className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-secondary-100"
                  placeholder="your@email.com"
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
                  autoComplete="new-password"
                  disabled={isLoading}
                  className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-secondary-100"
                  placeholder="At least 8 characters"
                />
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium mb-2">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  autoComplete="new-password"
                  disabled={isLoading}
                  className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-secondary-100"
                  placeholder="Confirm your password"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <UserPlus size={18} />
                {isLoading ? 'Creating account...' : 'Create Account'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-secondary-600">
                Already have an account?{' '}
                <Link href="/login" className="text-primary-600 hover:text-primary-700 font-medium">
                  Login here
                </Link>
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}
