import request from '@/utils/request'

export function fetchList(data) {
  console.log(data)
  return request({
    url: '/manager/list',
    method: 'post',
    data
  })
}

export function createManager(data) {
  return request({
    url: '/manager/create',
    method: 'post',
    data
  })
}

export function updateManager(data) {
  return request({
    url: '/manager/update',
    method: 'post',
    data
  })
}

