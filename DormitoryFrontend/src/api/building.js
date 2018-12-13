import request from '@/utils/request'

export function fetchList(query) {
  return request({
    url: '/building/list',
    method: 'post',
    params: query
  })
}

export function fetchAll() {
  return request({
    url: '/building/list/all',
    method: 'get'
  })
}

export function deleteBuilding(id) {
  return request({
    url: '/building/delete',
    method: 'get',
    params: { id }
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
