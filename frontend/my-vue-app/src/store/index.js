import { defineStore } from 'pinia'

export const useMainStore = defineStore('main', {
  state: () => ({
    user: null,
    posts: [],
    currentPost: null
  }),
  
  actions: {
    setUser(user) {
      this.user = user
    },
    
    setPosts(posts) {
      this.posts = posts
    },
    
    addPost(post) {
      this.posts.unshift(post)
    },
    
    setCurrentPost(post) {
      this.currentPost = post
    },
    
    addCommentToPost(postId, comment) {
      const post = this.posts.find(p => p.id === postId)
      if (post) {
        if (!post.comments) {
          post.comments = []
        }
        post.comments.push(comment)
      }
    },
    
    toggleLike(postId) {
      const post = this.posts.find(p => p.id === postId)
      if (post) {
        if (!post.likes) {
          post.likes = []
        }
        
        const likeIndex = post.likes.findIndex(like => like.user === this.user.id)
        if (likeIndex !== -1) {
          // 取消点赞
          post.likes.splice(likeIndex, 1)
        } else {
          // 添加点赞
          post.likes.push({
            user: this.user.id,
            post: postId
          })
        }
      }
    }
  }
})