import Mock from 'mockjs'
import { param2Obj } from '@/utils'

const List = []
const count = 100

for (let i = 0; i < count; i++) {
  List.push(Mock.mock({
    studentId: '@increment',
    name: '@first',
    'gender|1': ['男', '女'],
    enroll: '@datetime',
    birth: '@datetime',
    dormId: '@integer(1,255)',
    'department|1': ['教育学院', '心理学院', '文学院', '新闻传播学院', '历史文化学院', '马克思主义学院',
      '经济与工商管理学院', '公共管理学院', '法学院', '社会学院', '外国语学院', '教育信息技术学院',
      '信息管理学院', '体育学院', '音乐学院', '美术学院', '数学与统计学学院', '物理科学与技术学院',
      '化学学院', '生命科学学院', '计算机学院', '城市与环境科学学院', '国际文化交流学院', '政治与国际关系学院'],
    'status|1': ['未毕业', '已毕业'],
    buildingName: '东@integer(1,255)栋'
  }))
}

export default {
  getList: config => {
    const { buildingName, status, dormId, department, name, studentId, page = 1, limit = 20 } = param2Obj(config.url)
    const mockList = List.filter(item => {
      // console.log(item.buildingName)
      if (department !== '全部' && item.department !== department) { return false }
      if (status !== '全部' && item.status !== status) { return false }
      if (buildingName !== '全部' && item.buildingName !== buildingName) { return false }
      if (dormId && item.dormId !== +dormId) { return false }
      if (name && item.name !== name) {
        console.log(name)
        return false
      }
      if (studentId && +studentId !== item.studentId) return false
      console.log(item)
      return true
    })
    const pageList = mockList.filter((item, index) => index < limit * page && index >= limit * (page - 1))
    return {
      total: mockList.length,
      items: pageList
    }
  },
  deleteStudent: () => ({
    data: 'success'
  }),
  createStudent: () => ({
    data: 'success'
  }),
  updateStudent: () => ({
    data: 'success'
  })
}
