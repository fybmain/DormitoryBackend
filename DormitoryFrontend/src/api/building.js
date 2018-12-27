import request from '@/utils/request'

export function fetchList(data) {
  return request({
    url: '/building/list',
    method: 'post',
    data
  })
}

export function fetchAll() {
  return request({
    url: '/building/all',
    method: 'post'
  })
}

export function createBuilding(data) {
  return request({
    url: '/building/create',
    method: 'post',
    data
  })
}

export function updateBuilding(data) {
  return request({
    url: '/building/update',
    method: 'post',
    data
  })
}
