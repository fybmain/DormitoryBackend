import Mock from 'mockjs'
import { param2Obj } from '@/utils'

const List = []
const StuList = []
const count = 100

for (let i = 0; i < count; i++) {
  List.push(Mock.mock({
    DormNum: '@integer(1,999)',
    'BuildingName|1': ['东16栋', '东15栋', '东14栋', '东13栋', '东12栋', '东11栋', '东10栋'],
    WaterMeterId: '@integer(1,255)',
    ElectricMeterId: '@integer(1,255)'
  }))
}
for (let i = 0; i < 4; i++) {
  StuList.push(Mock.mock({
    Name: '@first',
    Studentid: '@integer(1,255)'
  }))
}

export default {
  getList: config => {
    const { DormNum, BuildingName, page = 1, limit = 20 } = param2Obj(config.url)
    console.log(param2Obj(config.url))
    const mockList = List.filter(item => {
      if (DormNum && DormNum !== '' && item.DormNum !== +DormNum) return false
      if (BuildingName && BuildingName !== '' && item.BuildingName !== BuildingName) return false
      return true
    })

    const pageList = mockList.filter((item, index) => index < limit * page && index >= limit * (page - 1))

    return {
      total: mockList.length,
      items: pageList
    }
  },
  getStudent: (config) => ({
    // const { dormNum, buildingId } = param2Obj(config.url)
    stuData: StuList
  }),
  createDormitory: () => ({
    data: 'success'
  }),
  updateDormitory: () => ({
    data: 'success'
  }),
  deleteDormitory: () => ({
    data: 'success'
  })
}
