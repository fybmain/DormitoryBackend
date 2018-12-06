import request from '@/utils/request'

export function fetchList(query) {
  return request({
    url: '/dormitory/list',
    method: 'post',
    params: query
  })
}

export function deleteDormitory(id) {
  return request({
    url: '/dormitory/delete',
    method: 'get',
    params: { id }
  })
}

export function createDormitory(data) {
  return request({
    url: '/dormitory/create',
    method: 'post',
    data
  })
}

export function updateDormitory(data) {
  return request({
    url: '/dormitory/update',
    method: 'post',
    data
  })
}
