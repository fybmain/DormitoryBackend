import request from '@/utils/request'

export function fetchList(query) {
  return request({
    url: '/dormitory/list',
    method: 'post',
    data: query
  })
}

export function deleteDormitory(id) {
  return request({
    url: '/dormitory/delete',
    method: 'post',
    data: {
      filter: { id }
    }
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
