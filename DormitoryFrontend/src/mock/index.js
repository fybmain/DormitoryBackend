import Mock from 'mockjs'
import loginAPI from './login'
import articleAPI from './article'
import studentAPI from './student'
import remoteSearchAPI from './remoteSearch'
import transactionAPI from './transaction'
import buildingAPI from './building'

// 修复在使用 MockJS 情况下，设置 withCredentials = true，且未被拦截的跨域请求丢失 Cookies 的问题
// https://github.com/nuysoft/Mock/issues/300
Mock.XHR.prototype.proxy_send = Mock.XHR.prototype.send
Mock.XHR.prototype.send = function() {
  if (this.custom.xhr) {
    this.custom.xhr.withCredentials = this.withCredentials || false
  }
  this.proxy_send(...arguments)
}

// Mock.setup({
//   timeout: '350-600'
// })

// 登录相关
Mock.mock(/\/login\/login/, 'post', loginAPI.loginByUsername)
Mock.mock(/\/login\/logout/, 'post', loginAPI.logout)
Mock.mock(/\/user\/info\.*/, 'get', loginAPI.getUserInfo)

// 文章相关
Mock.mock(/\/article\/list/, 'get', articleAPI.getList)
Mock.mock(/\/article\/detail/, 'get', articleAPI.getArticle)
Mock.mock(/\/article\/pv/, 'get', articleAPI.getPv)
Mock.mock(/\/article\/create/, 'post', articleAPI.createArticle)
Mock.mock(/\/article\/update/, 'post', articleAPI.updateArticle)

// 学生相关
Mock.mock(/\/student\/list/, 'get', studentAPI.getList)
Mock.mock(/\/student\/delete/, 'post', studentAPI.deleteStudent)
Mock.mock(/\/student\/create/, 'post', studentAPI.createStudent)
Mock.mock(/\/student\/update/, 'post', studentAPI.updateStudent)

// 建筑相关
Mock.mock(/\/building\/list/, 'post', buildingAPI.getList)
Mock.mock(/\/building\/delete/, 'get', buildingAPI.deleteBuilding)
Mock.mock(/\/building\/create/, 'post', buildingAPI.createBuilding)
Mock.mock(/\/building\/update/, 'post', buildingAPI.updateBuilding)

// 搜索相关/building/list/all
Mock.mock(/\/search\/user/, 'get', remoteSearchAPI.searchUser)

// 账单相关
Mock.mock(/\/transaction\/list/, 'get', transactionAPI.getList)

export default Mock
