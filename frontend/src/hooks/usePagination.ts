import { useState, useCallback, useMemo } from 'react'
import { DEFAULT_PAGE_SIZE } from '@/utils/constants'

interface UsePaginationOptions {
  initialPage?: number
  initialPageSize?: number
  total?: number
}

interface UsePaginationReturn {
  page: number
  pageSize: number
  total: number
  totalPages: number
  hasNext: boolean
  hasPrevious: boolean
  goToPage: (page: number) => void
  nextPage: () => void
  previousPage: () => void
  setPageSize: (size: number) => void
  setTotal: (total: number) => void
  reset: () => void
}

export const usePagination = (options: UsePaginationOptions = {}): UsePaginationReturn => {
  const {
    initialPage = 1,
    initialPageSize = DEFAULT_PAGE_SIZE,
    total: initialTotal = 0,
  } = options

  const [page, setPage] = useState(initialPage)
  const [pageSize, setPageSize] = useState(initialPageSize)
  const [total, setTotal] = useState(initialTotal)

  const totalPages = useMemo(() => {
    return Math.ceil(total / pageSize)
  }, [total, pageSize])

  const hasNext = useMemo(() => {
    return page < totalPages
  }, [page, totalPages])

  const hasPrevious = useMemo(() => {
    return page > 1
  }, [page])

  const goToPage = useCallback(
    (newPage: number) => {
      if (newPage >= 1 && newPage <= totalPages) {
        setPage(newPage)
      }
    },
    [totalPages]
  )

  const nextPage = useCallback(() => {
    if (hasNext) {
      setPage(prev => prev + 1)
    }
  }, [hasNext])

  const previousPage = useCallback(() => {
    if (hasPrevious) {
      setPage(prev => prev - 1)
    }
  }, [hasPrevious])

  const handleSetPageSize = useCallback((size: number) => {
    setPageSize(size)
    setPage(1) // Reset to first page when changing page size
  }, [])

  const reset = useCallback(() => {
    setPage(initialPage)
    setPageSize(initialPageSize)
    setTotal(initialTotal)
  }, [initialPage, initialPageSize, initialTotal])

  return {
    page,
    pageSize,
    total,
    totalPages,
    hasNext,
    hasPrevious,
    goToPage,
    nextPage,
    previousPage,
    setPageSize: handleSetPageSize,
    setTotal,
    reset,
  }
}

export default usePagination
