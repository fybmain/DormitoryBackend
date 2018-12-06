import Mock from 'mockjs'
import { param2Obj } from '@/utils'

const List = []
const count = 100

for (let i = 0; i < count; i++) {
  List.push(Mock.mock({
    id: '@increment',
    BuildingName: '东@integer(1,255)栋'
  }))
}

export default {
  getList: config => {
    const { buildingName, page = 1, limit = 20 } = param2Obj(config.url)
    console.log(param2Obj(config.url))
    const mockList = List.filter(item => {
      if (buildingName && buildingName !== '' && item.buildingName !== buildingName) return false
      return true
    })

    const pageList = mockList.filter((item, index) => index < limit * page && index >= limit * (page - 1))

    return {
      total: mockList.length,
      items: pageList
    }
  },
  createBuilding: () => ({
    data: 'success'
  }),
  updateBuilding: () => ({
    data: 'success'
  }),
  deleteBuilding: () => ({
    data: 'success'
  })
}
