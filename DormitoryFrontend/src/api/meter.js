import request from '@/utils/request'

export function createElectricity(data) {
  return request({
    url: '/electricity_bill/create',
    method: 'post',
    data
  })
}

export function fetchElectricity(data) {
  return request({
    url: '/electricity_bill/list',
    method: 'post',
    data
  })
}

export function updateElectricity(data) {
  return request({
    url: '/electricity_bill/update',
    method: 'post',
    data
  })
}

export function createWater(data) {
  return request({
    url: '/water_bill/create',
    method: 'post',
    data
  })
}

export function fetchWater(data) {
  return request({
    url: '/water_bill/list',
    method: 'post',
    data
  })
}

export function updateWater(data) {
  return request({
    url: '/water_bill/update',
    method: 'post',
    data
  })
}
