import request from '@/utils/request'

export function fetchList(data) {
  return request({
    url: '/dormitory/list',
    method: 'post',
    data
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

export function fetchDepartment() {
  return request({
    url: '/department/all',
    method: 'post'
  })
}
