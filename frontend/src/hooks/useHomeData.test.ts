import { renderHook, waitFor } from '@testing-library/react'
  import { describe, it, expect, vi, afterEach } from 'vitest'
  import { useHomeData } from './useHomeData'

  describe('useHomeData', () => {
    afterEach(() => {
      vi.unstubAllGlobals()
    })

    it('returns startups from the API', async () => {
      const apiData = {
        count: 1,
        next: null,
        previous: null,
        results: [
          {
            startup_id: 1,
            startup_name: 'Handmade Co',
            short_description: 'Woodwork and ceramics',
            logo: '/media/thumbs/1.jpg',
            location: 'Chernivtsi',
            industries: ['craft'],
          },
        ],
      }
     vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => apiData }))

      const { result } = renderHook(() => useHomeData())

      await waitFor(() => expect(result.current.isLoading).toBe(false))
      expect(result.current.startups?.results[0].company_name).toBe('Handmade Co')
      expect(result.current.error).toBeNull()
    })

    it('sets error and null startups when the API fails', async () => {
      vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network')))

      const { result } = renderHook(() => useHomeData())

      await waitFor(() => expect(result.current.isLoading).toBe(false))
      expect(result.current.startups).toBeNull()
      expect(result.current.error).toBe('network')
    })
})
