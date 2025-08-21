'use client'

export default function ProfileSkeleton() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <div className="max-w-6xl mx-auto">
          
          <div className="mb-12">
            <div className="relative overflow-hidden bg-white dark:bg-gray-800 rounded-3xl shadow-xl shadow-blue-100/50 dark:shadow-blue-900/20 border border-blue-100/20 dark:border-blue-800/20 animate-pulse">
              <div className="px-6 sm:px-8 lg:px-12 py-8 sm:py-12">
                <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 sm:gap-8">
                  <div className="relative">
                    <div className="h-24 w-24 sm:h-28 sm:w-28 rounded-2xl bg-gray-300 dark:bg-gray-700"></div>
                  </div>
                  
                  <div className="flex-1 text-center sm:text-left space-y-3">
                    <div className="h-8 bg-gray-300 dark:bg-gray-700 rounded-lg w-48 mx-auto sm:mx-0"></div>
                    <div className="h-5 bg-gray-200 dark:bg-gray-600 rounded-lg w-64 mx-auto sm:mx-0"></div>
                    <div className="flex flex-wrap justify-center sm:justify-start gap-3">
                      <div className="h-7 w-24 bg-gray-200 dark:bg-gray-600 rounded-full"></div>
                      <div className="h-7 w-20 bg-gray-200 dark:bg-gray-600 rounded-full"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <div className="lg:col-span-2 space-y-8">
              
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg shadow-gray-100/50 dark:shadow-black/20 border border-gray-100/50 dark:border-gray-700/50 overflow-hidden animate-pulse">
                <div className="px-6 sm:px-8 py-6 bg-gradient-to-r from-gray-50 to-blue-50/30 dark:from-gray-700/50 dark:to-blue-900/20 border-b border-gray-100 dark:border-gray-700">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
                    <div className="h-6 w-48 bg-gray-300 dark:bg-gray-600 rounded-lg"></div>
                  </div>
                </div>
                <div className="p-6 sm:p-8">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    {Array(2).fill(0).map((_, i) => (
                      <div key={i} className="space-y-3">
                        <div className="flex items-center gap-2">
                          <div className="h-4 w-4 bg-gray-200 dark:bg-gray-600 rounded"></div>
                          <div className="h-4 w-16 bg-gray-200 dark:bg-gray-600 rounded"></div>
                        </div>
                        <div className="bg-gray-100 dark:bg-gray-700/50 rounded-xl px-4 py-3">
                          <div className="h-4 w-32 bg-gray-300 dark:bg-gray-600 rounded"></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg shadow-gray-100/50 dark:shadow-black/20 border border-gray-100/50 dark:border-gray-700/50 overflow-hidden animate-pulse">
                <div className="px-6 sm:px-8 py-6 bg-gradient-to-r from-gray-50 to-purple-50/30 dark:from-gray-700/50 dark:to-purple-900/20 border-b border-gray-100 dark:border-gray-700">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
                    <div className="h-6 w-32 bg-gray-300 dark:bg-gray-600 rounded-lg"></div>
                  </div>
                </div>
                <div className="p-6 sm:p-8">
                  <div className="flex flex-wrap gap-3">
                    {Array(5).fill(0).map((_, i) => (
                      <div key={i} className="h-8 w-24 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-8">
              
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg shadow-gray-100/50 dark:shadow-black/20 border border-gray-100/50 dark:border-gray-700/50 overflow-hidden animate-pulse">
                <div className="px-6 py-6 bg-gradient-to-r from-gray-50 to-green-50/30 dark:from-gray-700/50 dark:to-green-900/20 border-b border-gray-100 dark:border-gray-700">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
                    <div className="h-5 w-32 bg-gray-300 dark:bg-gray-600 rounded-lg"></div>
                  </div>
                </div>
                <div className="p-6 space-y-4">
                  {Array(4).fill(0).map((_, i) => (
                    <div key={i} className="p-4 rounded-xl border border-gray-100 dark:border-gray-700">
                      <div className="flex items-center justify-between mb-2">
                        <div className="h-8 w-12 bg-gray-300 dark:bg-gray-600 rounded"></div>
                        <div className="h-4 w-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                      </div>
                      <div className="h-3 w-20 bg-gray-200 dark:bg-gray-600 rounded"></div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg shadow-gray-100/50 dark:shadow-black/20 border border-gray-100/50 dark:border-gray-700/50 overflow-hidden animate-pulse">
                <div className="px-6 py-6 bg-gradient-to-r from-gray-50 to-orange-50/30 dark:from-gray-700/50 dark:to-orange-900/20 border-b border-gray-100 dark:border-gray-700">
                  <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded-lg bg-gray-200 dark:bg-gray-700"></div>
                    <div className="h-5 w-28 bg-gray-300 dark:bg-gray-600 rounded-lg"></div>
                  </div>
                </div>
                <div className="p-6 space-y-3">
                  {Array(3).fill(0).map((_, i) => (
                    <div key={i} className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl bg-gray-100 dark:bg-gray-700">
                      <div className="h-4 w-4 bg-gray-300 dark:bg-gray-600 rounded"></div>
                      <div className="h-4 w-24 bg-gray-300 dark:bg-gray-600 rounded"></div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
