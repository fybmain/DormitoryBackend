<template>
  <div class="app-container">
    <div class="filter-container">
      <el-row type="flex" class="row-bg" justify="end">
        <el-col>
          <el-input :placeholder="$t('student.studentid')" v-model="listQuery.studentId" style="width: 100px;" class="filter-item" @keyup.enter.native="handleFilter"/>
          <el-input :placeholder="$t('student.name')" v-model="listQuery.name" style="width: 100px;" class="filter-item" @keyup.enter.native="handleFilter"/>
          <el-select v-model="listQuery.department" :placeholder="$t('student.department')" clearable style="width: 170px" class="filter-item">
            <el-option v-for="item in departmentOptions" :key="item" :label="item" :value="item"/>
          </el-select>
          <el-select v-model="listQuery.status" :placeholder="$t('student.status')" clearable style="width: 100px" class="filter-item">
            <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item"/>
          </el-select>
          <el-select v-model="listQuery.buildingName" :placeholder="$t('student.buildingname')" clearable style="width: 100px" class="filter-item">
            <el-option v-for="item in buildingOptions" :key="item" :label="item" :value="item"/>
          </el-select>
          <el-input :placeholder="$t('student.dormid')" v-model="listQuery.dormId" style="width: 100px;" class="filter-item" @keyup.enter.native="handleFilter"/>
          <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">{{ $t('student.search') }}</el-button>
        </el-col>
        <el-col align="right">
          <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-edit" @click="handleCreate">{{ $t('student.add') }}</el-button>
          <el-button v-waves :loading="downloadLoading" class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">{{ $t('student.export') }}</el-button>
        </el-col>
      </el-row>
    </div>

    <el-table
      v-loading="listLoading"
      :key="tableKey"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;">
      <el-table-column :label="$t('student.studentid')" prop="studentid" align="center" width="80">
        <template slot-scope="scope">
          <span>{{ scope.row.studentId }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.name')" align="center" width="150px">
        <template slot-scope="scope">
          <span>{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.gender')" width="110px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.gender }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.enroll')" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.enroll | parseTime('{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.birth')" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.birth | parseTime('{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column v-permission="['admin']" :label="$t('student.buildingname')" width="110px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.buildingName }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.dormid')" width="110px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.dormId }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.department')" align="center" width="100px">
        <template slot-scope="scope">
          <span>{{ scope.row.department }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.status')" class-name="status-col" width="100">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status | statusFilter">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.actions')" align="center" min-width="230" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button type="primary" size="mini" @click="handleUpdate(scope.row)">{{ $t('student.edit') }}</el-button>
          <el-button v-if="scope.row.status!='已毕业'" size="mini" type="success" @click="handleModifyStatus(scope.row,'已毕业')">{{ $t('student.graduate') }}
          </el-button>
          <el-button v-if="scope.row.status!='未毕业'" size="mini" @click="handleModifyStatus(scope.row,'未毕业')">{{ $t('student.ungraduate') }}
          </el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">{{ $t('student.delete') }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="80px" style="width: 400px; margin-left:50px;">
        <el-form-item :label="$t('student.name')" prop="name">
          <el-input v-model="temp.name"/>
        </el-form-item>
        <el-form-item :label="$t('student.studentid')" prop="studentId">
          <el-input v-model="temp.studentId"/>
        </el-form-item>
        <el-form-item :label="$t('student.gender')" prop="gender">
          <el-input v-model="temp.gender"/>
        </el-form-item>
        <el-form-item :label="$t('student.department')" prop="department">
          <el-select v-model="temp.department" class="filter-item" placeholder="Please select">
            <el-option v-for="item in departmentOptions" :key="item" :label="item" :value="item"/>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('student.birth')" prop="birth">
          <el-date-picker v-model="temp.birth" type="datetime" placeholder="Please pick a date"/>
        </el-form-item>
        <el-form-item :label="$t('student.enroll')" prop="enroll">
          <el-date-picker v-model="temp.enroll" type="datetime" placeholder="Please pick a date"/>
        </el-form-item>
        <el-form-item :label="$t('student.dormid')">
          <el-select v-model="temp.dormId" class="filter-item" placeholder="Please select">
            <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item"/>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('student.buildingname')">
          <el-select v-model="temp.buildingName" class="filter-item" placeholder="Please select">
            <el-option v-for="item in buildingOptions" :key="item" :label="item" :value="item"/>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">{{ $t('student.cancel') }}</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">{{ $t('student.confirm') }}</el-button>
      </div>
    </el-dialog>

  </div>
</template>

<script>
import { fetchList, createArticle, updateArticle } from '@/api/student'
import { fetchBuildingList } from '@/api/building'
import permission from '@/directive/permission/index.js'
import waves from '@/directive/waves' // Waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // Secondary package based on el-pagination

export default {
  name: 'Student',
  components: { Pagination },
  directives: { waves, permission },
  filters: {
    statusFilter(status) {
      const statusMap = {
        '未毕业': 'success',
        '已毕业': 'danger'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      tableKey: 0,
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        department: '全部',
        status: '全部',
        name: undefined,
        studentId: undefined,
        dormId: undefined,
        buildingName: '全部'
      },
      departmentOptions: ['全部', '教育学院', '心理学院', '文学院', '新闻传播学院', '历史文化学院', '马克思主义学院',
        '经济与工商管理学院', '公共管理学院', '法学院', '社会学院', '外国语学院', '教育信息技术学院',
        '信息管理学院', '体育学院', '音乐学院', '美术学院', '数学与统计学学院', '物理科学与技术学院',
        '化学学院', '生命科学学院', '计算机学院', '城市与环境科学学院', '国际文化交流学院', '政治与国际关系学院'],
      statusOptions: ['全部', '已毕业', '未毕业'],
      buildingOptions: ['全部'],
      temp: {
        studentId: undefined,
        name: '',
        gender: undefined,
        department: '',
        enroll: undefined,
        birth: '',
        dormId: undefined,
        status: '未毕业',
        buildingName: ''
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '修改',
        create: '创建'
      },
      rules: {
        name: [{ required: true, message: 'name is required', trigger: 'change' }],
        studentId: [{ required: true, message: 'student id is required', trigger: 'change' }],
        gender: [{ required: true, message: 'name is required', trigger: 'change' }],
        department: [{ required: true, message: 'department is required', trigger: 'change' }],
        birth: [{ type: 'date', required: true, message: 'birth is required', trigger: 'change' }],
        enroll: [{ type: 'date', required: true, message: 'enroll is required', trigger: 'change' }],
        dormId: [{ required: true, message: 'dorm id is required', trigger: 'change' }],
        buildingName: [{ required: true, message: 'building name is required', trigger: 'change' }]
      },
      downloadLoading: false
    }
  },
  created() {
    this.getList()
    this.getBuilding()
  },
  methods: {
    getList() {
      this.listLoading = true
      fetchList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total

        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    },
    getBuilding() {
      fetchBuildingList().then(response => {
        for (var j = 0, len = response.data.items.length; j < len; j++) {
          this.buildingOptions.push(response.data.items[j].buildingName)
        }
        this.buildingOptions = this.buildingOptions.filter(function(element, index, self) {
          return self.indexOf(element) === index
        })
        console.log(this.buildingOptions)
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleModifyStatus(row, status) {
      this.$message({
        message: '操作成功',
        type: 'success'
      })
      row.status = status
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        department: undefined,
        name: '',
        status: '未毕业',
        dormid: undefined,
        buildingname: '全部'
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.temp.id = parseInt(Math.random() * 100) + 1024 // mock a id
          this.temp.author = 'vue-element-admin'
          createArticle(this.temp).then(() => {
            this.list.unshift(this.temp)
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '创建成功',
              type: 'success',
              duration: 2000
            })
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.temp.timestamp = new Date(this.temp.timestamp)
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          tempData.timestamp = +new Date(tempData.timestamp) // change Thu Nov 30 2017 16:41:05 GMT+0800 (CST) to 1512031311464
          updateArticle(tempData).then(() => {
            for (const v of this.list) {
              if (v.id === this.temp.id) {
                const index = this.list.indexOf(v)
                this.list.splice(index, 1, this.temp)
                break
              }
            }
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
          })
        }
      })
    },
    handleDelete(row) {
      this.$notify({
        title: '成功',
        message: '删除成功',
        type: 'success',
        duration: 2000
      })
      const index = this.list.indexOf(row)
      this.list.splice(index, 1)
    },
    handleDownload() {
      this.downloadLoading = true
      import('@/vendor/Export2Excel').then(excel => {
        const tHeader = ['timestamp', 'name', 'type', 'department', 'status']
        const filterVal = ['timestamp', 'name', 'type', 'department', 'status']
        const data = this.formatJson(filterVal, this.list)
        excel.export_json_to_excel({
          header: tHeader,
          data,
          filename: 'table-list'
        })
        this.downloadLoading = false
      })
    },
    formatJson(filterVal, jsonData) {
      return jsonData.map(v => filterVal.map(j => {
        if (j === 'timestamp') {
          return parseTime(v[j])
        } else {
          return v[j]
        }
      }))
    }
  }
}
</script>
