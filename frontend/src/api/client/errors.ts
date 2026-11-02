// Field errors from DRF: {"email": ["Enter a valid email address."]}
export type FieldErrors = Record<string, string[]>

export const NETWORK_ERROR_STATUS = 0

// Any failed API request: an error status from the backend or no response at all
export class ApiError extends Error {
  status: number
  fieldErrors: FieldErrors
  // Seconds from the Retry-After header (429), if the backend sent it
  retryAfter: number | null

  constructor(
    status: number,
    message: string,
    fieldErrors: FieldErrors = {},
    retryAfter: number | null = null,
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.fieldErrors = fieldErrors
    this.retryAfter = retryAfter
  }
}
