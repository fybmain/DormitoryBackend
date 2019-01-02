import request from '@/utils/request'

export function fetchList(data) {
  console.log(data)
  return request({
    url: '/dormitoryrating/list',
    method: 'post',
    data
  })
}

export function createRating(data) {
  return request({
    url: '/dormitoryrating/create',
    method: 'post',
    data
  })
}

export function updateRating(data) {
  return request({
    url: '/dormitoryrating/update',
    method: 'post',
    data
  })
}
