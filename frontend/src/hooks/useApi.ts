import { useState, useCallback } from 'react'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<T>
  reset: () => void
}

// Generic hook for API calls
export const useApi = <T = any>(
  apiFunc: (...args: any[]) => Promise<any>
): UseApiReturn<T> => {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  const execute = useCallback(
    async (...args: any[]): Promise<T> => {
      setState({ data: null, loading: true, error: null })

      try {
        const response = await apiFunc(...args)
        const data = response.data || response
        setState({ data, loading: false, error: null })
        return data
      } catch (error) {
        const err = error instanceof Error ? error : new Error('Unknown error')
        setState({ data: null, loading: false, error: err })
        throw err
      }
    },
    [apiFunc]
  )

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null })
  }, [])

  return {
    ...state,
    execute,
    reset,
  }
}

export default useApi
