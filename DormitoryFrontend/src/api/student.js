import request from '@/utils/request'

export function fetchList(query) {
  console.log(query)
  return request({
    url: '/student/list',
    method: 'get',
    params: query
  })
}

export function fetchArticle(id) {
  return request({
    url: '/student/detail',
    method: 'get',
    params: { id }
  })
}

export function fetchPv(pv) {
  return request({
    url: '/student/pv',
    method: 'get',
    params: { pv }
  })
}

export function createArticle(data) {
  return request({
    url: '/student/create',
    method: 'post',
    data
  })
}

export function updateArticle(data) {
  return request({
    url: '/student/update',
    method: 'post',
    data
  })
}
