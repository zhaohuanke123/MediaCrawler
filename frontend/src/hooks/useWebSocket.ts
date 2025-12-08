import { useEffect, useRef, useState, useCallback } from 'react'
import { WS_BASE_URL } from '@/utils/constants'

interface UseWebSocketOptions {
  onOpen?: (event: Event) => void
  onMessage?: (event: MessageEvent) => void
  onError?: (event: Event) => void
  onClose?: (event: CloseEvent) => void
  reconnect?: boolean
  reconnectInterval?: number
  reconnectAttempts?: number
}

interface UseWebSocketReturn {
  connected: boolean
  send: (data: any) => void
  close: () => void
}

export const useWebSocket = (
  url: string,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn => {
  const {
    onOpen,
    onMessage,
    onError,
    onClose,
    reconnect = true,
    reconnectInterval = 3000,
    reconnectAttempts = 5,
  } = options

  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectCountRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const connect = useCallback(() => {
    try {
      const wsUrl = url.startsWith('ws') ? url : `${WS_BASE_URL}${url}`
      const ws = new WebSocket(wsUrl)

      ws.onopen = (event) => {
        console.log('WebSocket connected:', url)
        setConnected(true)
        reconnectCountRef.current = 0
        onOpen?.(event)
      }

      ws.onmessage = (event) => {
        onMessage?.(event)
      }

      ws.onerror = (event) => {
        console.error('WebSocket error:', event)
        onError?.(event)
      }

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event)
        setConnected(false)
        wsRef.current = null
        onClose?.(event)

        // Attempt to reconnect
        if (reconnect && reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current++
          console.log(`Reconnecting... Attempt ${reconnectCountRef.current}`)
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval)
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
    }
  }, [url, onOpen, onMessage, onError, onClose, reconnect, reconnectInterval, reconnectAttempts])

  const send = useCallback((data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message = typeof data === 'string' ? data : JSON.stringify(data)
      wsRef.current.send(message)
    } else {
      console.warn('WebSocket is not connected. Cannot send message.')
    }
  }, [])

  const close = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  useEffect(() => {
    connect()

    return () => {
      close()
    }
  }, [connect, close])

  return {
    connected,
    send,
    close,
  }
}

export default useWebSocket
