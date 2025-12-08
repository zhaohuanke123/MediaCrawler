import { useState, useCallback, ChangeEvent } from 'react'

interface UseFormOptions<T> {
  initialValues: T
  onSubmit?: (values: T) => void | Promise<void>
  validate?: (values: T) => Record<string, string>
}

interface UseFormReturn<T> {
  values: T
  errors: Record<string, string>
  touched: Record<string, boolean>
  isSubmitting: boolean
  handleChange: (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void
  handleBlur: (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => void
  handleSubmit: (e?: React.FormEvent) => Promise<void>
  setFieldValue: (field: string, value: any) => void
  setFieldError: (field: string, error: string) => void
  setValues: (values: T) => void
  resetForm: () => void
  isValid: boolean
}

export const useForm = <T extends Record<string, any>>(
  options: UseFormOptions<T>
): UseFormReturn<T> => {
  const { initialValues, onSubmit, validate } = options

  const [values, setValues] = useState<T>(initialValues)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    const checked = (e.target as HTMLInputElement).checked

    setValues(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[name]
        return newErrors
      })
    }
  }, [errors])

  const handleBlur = useCallback((e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name } = e.target
    setTouched(prev => ({ ...prev, [name]: true }))
  }, [])

  const handleSubmit = useCallback(async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault()
    }

    // Mark all fields as touched
    const allTouched = Object.keys(values).reduce((acc, key) => {
      acc[key] = true
      return acc
    }, {} as Record<string, boolean>)
    setTouched(allTouched)

    // Validate
    const validationErrors = validate ? validate(values) : {}
    setErrors(validationErrors)

    // If no errors, submit
    if (Object.keys(validationErrors).length === 0 && onSubmit) {
      setIsSubmitting(true)
      try {
        await onSubmit(values)
      } catch (error) {
        console.error('Form submission error:', error)
      } finally {
        setIsSubmitting(false)
      }
    }
  }, [values, validate, onSubmit])

  const setFieldValue = useCallback((field: string, value: any) => {
    setValues(prev => ({ ...prev, [field]: value }))
  }, [])

  const setFieldError = useCallback((field: string, error: string) => {
    setErrors(prev => ({ ...prev, [field]: error }))
  }, [])

  const resetForm = useCallback(() => {
    setValues(initialValues)
    setErrors({})
    setTouched({})
    setIsSubmitting(false)
  }, [initialValues])

  const isValid = Object.keys(errors).length === 0

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    setFieldError,
    setValues,
    resetForm,
    isValid,
  }
}

export default useForm
