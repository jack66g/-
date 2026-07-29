import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  // 从 localStorage 初始化，防止刷新页面掉线
  const token = ref(localStorage.getItem('token') || '')
  const role = ref(localStorage.getItem('role') || '')
  const username = ref(localStorage.getItem('username') || '')

  const setAuth = (newToken, newRole, newName) => {
    token.value = newToken
    role.value = newRole
    username.value = newName
    localStorage.setItem('token', newToken)
    localStorage.setItem('role', newRole)
    localStorage.setItem('username', newName)
  }

  const clearAuth = () => {
    token.value = ''
    role.value = ''
    username.value = ''
    localStorage.clear()
  }

  return { token, role, username, setAuth, clearAuth }
})
