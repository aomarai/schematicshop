import { useState } from 'react'
import { motion } from 'framer-motion'
import { Chrome, Github, MessageCircle } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface SocialLoginButtonsProps {
  mode: 'login' | 'register'
}

export default function SocialLoginButtons({ mode }: SocialLoginButtonsProps) {
  const [loading, setLoading] = useState<string | null>(null)

  const handleSocialLogin = (provider: string) => {
    setLoading(provider)
    // Redirect to Django allauth social login
    window.location.href = `${API_URL}/accounts/${provider}/login/?process=login`
  }

  const socialProviders = [
    {
      id: 'google',
      name: 'Google',
      icon: Chrome,
      color: 'bg-white hover:bg-gray-50 text-gray-900 border border-gray-300',
    },
    {
      id: 'github',
      name: 'GitHub',
      icon: Github,
      color: 'bg-gray-900 hover:bg-gray-800 text-white',
    },
    {
      id: 'discord',
      name: 'Discord',
      icon: MessageCircle,
      color: 'bg-indigo-600 hover:bg-indigo-700 text-white',
    },
  ]

  return (
    <div className="space-y-3">
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-secondary-300"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-secondary-500">
            Or {mode} with
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {socialProviders.map((provider) => {
          const Icon = provider.icon
          return (
            <motion.button
              key={provider.id}
              type="button"
              onClick={() => handleSocialLogin(provider.id)}
              disabled={loading !== null}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`
                w-full px-4 py-3 rounded-lg font-medium
                flex items-center justify-center gap-3
                transition-colors duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
                ${provider.color}
              `}
            >
              <Icon size={20} />
              {loading === provider.id ? (
                <span>Connecting...</span>
              ) : (
                <span>Continue with {provider.name}</span>
              )}
            </motion.button>
          )
        })}
      </div>

      <p className="text-xs text-center text-secondary-500 mt-4">
        By continuing, you agree to our Terms of Service and Privacy Policy
      </p>
    </div>
  )
}
