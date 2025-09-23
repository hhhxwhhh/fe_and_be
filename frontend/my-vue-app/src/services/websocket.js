class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000;
    this.listeners = {};
    this.pingInterval = null;
    this.isConnecting = false;
  }

  connect() {
    // 防止重复连接
    if (this.isConnecting || this.isConnected) {
      return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
      console.error('No token available for WebSocket connection');
      this.emit('error', new Error('No authentication token available'));
      return;
    }

    this.isConnecting = true;
    
    // 使用正确的WebSocket协议连接
    const wsUrl = `ws://localhost:8000/ws/chat/?token=${token}`;
    console.log('Connecting to WebSocket:', wsUrl);
    
    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        
        // 启动心跳检测
        this.startPing();
        
        this.emit('connected');
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit('message', data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket disconnected. Code:', event.code, 'Reason:', event.reason);
        this.isConnected = false;
        this.isConnecting = false;
        this.stopPing();
        this.emit('disconnected');
        
        // 只有在非正常关闭的情况下才尝试重连
        if (event.code !== 1000) { // 1000是正常关闭
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
              console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
              this.connect();
            }, this.reconnectInterval);
          } else {
            console.error('Max reconnect attempts reached. Giving up.');
            this.emit('error', new Error('Failed to connect to WebSocket after multiple attempts'));
          }
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
        this.emit('error', error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.isConnecting = false;
      this.emit('error', error);
    }
  }

  disconnect() {
    if (this.socket) {
      this.stopPing();
      this.socket.close(1000, 'Client disconnect'); // 正常关闭
      this.isConnected = false;
      this.isConnecting = false;
    }
  }

  sendMessage(recipientId, content, messageType = 'text') {
    if (this.isConnected && this.socket) {
      const message = {
        type: 'message',
        recipient_id: recipientId,
        content: content,
        message_type: messageType
      };
      this.socket.send(JSON.stringify(message));
      return Promise.resolve();
    } else {
      console.error('WebSocket is not connected');
      return Promise.reject(new Error('WebSocket is not connected. Please check your connection.'));
    }
  }

  // 发送群聊消息
  sendGroupMessage(groupId, formData) {
    if (this.isConnected && this.socket) {
      // 将FormData转换为对象
      const message = {
        type: 'group_message',
        group_id: groupId,
        content: formData.get('content') || '',
        file: formData.get('file'),
        image: formData.get('image')
      };
      
      this.socket.send(JSON.stringify(message));
      return Promise.resolve();
    } else {
      console.error('WebSocket is not connected');
      return Promise.reject(new Error('WebSocket is not connected. Please check your connection.'));
    }
  }

  markAsRead(messageId) {
    if (this.isConnected && this.socket) {
      const message = {
        type: 'read',
        message_id: messageId
      };
      this.socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  // 心跳检测
  startPing() {
    this.pingInterval = setInterval(() => {
      if (this.isConnected && this.socket) {
        this.socket.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // 每30秒发送一次心跳
  }

  stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
  }
}

export default new WebSocketService();