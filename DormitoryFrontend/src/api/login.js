import request from '@/utils/request'

export function loginByUsername(account, password, role) {
  const data = {
    account,
    password,
    role
  }
  console.log(data)
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

export function logout() {
  return request({
    url: '/login/logout',
    method: 'post'
  })
}

export function getUserInfo(token) {
  const data = {
    token
  }
  return request({
    url: '/auth/getinfo',
    method: 'post',
    data
  })
}

