import request from '@/utils/request'

export function fetchList(query) {
  return request({
    url: '/student/list',
    method: 'post',
    params: query
  })
}

export function createStudent(data) {
  return request({
    url: '/student/create',
    method: 'post',
    data
  })
}

export function updateStudent(data) {
  return request({
    url: '/student/update',
    method: 'post',
    data
  })
}

export function deleteStudent(data) {
  return request({
    url: '/student/delete',
    method: 'post',
    data
  })
}
