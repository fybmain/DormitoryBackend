<template>
  <div class="app-container">
    <div class="filter-container">
      <el-row type="flex" class="row-bg" justify="end">
        <el-col>
          <el-input :placeholder="$t('student.studentid')" v-model="listQuery.filter.card_id" style="width: 100px;" class="filter-item" @keyup.enter.native="handleFilter"/>
          <el-input :placeholder="$t('student.name')" v-model="listQuery.filter.real_name" style="width: 100px;" class="filter-item" @keyup.enter.native="handleFilter"/>
          <el-select v-model="listQuery.filter.department" :placeholder="$t('student.department')" clearable style="width: 170px" class="filter-item">
            <el-option v-for="item in departmentOptions" :key="item" :label="item" :value="item"/>
          </el-select>
          <el-select v-model="listQuery.filter.buildingName" :placeholder="$t('student.buildingname')" clearable style="width: 100px" class="filter-item">
            <el-option v-for="item in buildingOptions" :key="item" :label="item" :value="item"/>
          </el-select>
          <el-input :placeholder="$t('student.dormid')" v-model="listQuery.filter.dormitoryid" style="width: 100px;" class="filter-item" @keyup.enter.native="handleFilter"/>
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
      <el-table-column :label="$t('student.studentid')" prop="studentid" align="center" width="150px">
        <template slot-scope="scope">
          <span>{{ scope.row.card_id }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.name')" align="center" width="150px">
        <template slot-scope="scope">
          <span>{{ scope.row.real_name }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.gender')" width="110px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.gender }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.enroll')" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.enroll_date | parseTime('{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.birth')" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.birth_date | parseTime('{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.buildingname')" width="110px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.dormitory.building.name }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.dormid')" width="110px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.dormitory.number }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.department')" align="center" width="100px">
        <template slot-scope="scope">
          <span>{{ scope.row.department.name }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('student.actions')" align="center" min-width="230" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button type="primary" size="mini" @click="handleUpdate(scope.row)">{{ $t('student.edit') }}</el-button>
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
        <el-form-item :label="$t('student.buildingname')">
          <el-select v-model="temp.buildingName" class="filter-item" placeholder="Please select" @change="handleUpdateDorm(temp.buildingName)" >
            <el-option v-for="item in buildingOptions" :key="item" :label="item" :value="item"/>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('student.dormid')">
          <el-select v-model="temp.dormId" class="filter-item" placeholder="Please select">
            <el-option v-for="item in dormOptions" :key="item" :label="item" :value="item"/>
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
import { fetchList as fetchStudentList, createStudent, updateStudent, deleteStudent } from '@/api/student'
import { fetchAll as fetchBuildingList } from '@/api/building'
import { fetchDepartment } from '@/api/dormitory'
import { fetchList as fetchDormitoryList } from '@/api/dormitory'
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
        filter: {
          department_name: undefined,
          real_name: undefined,
          card_id: undefined,
          dormitory: undefined,
          building_name: undefined
        }
      },
      departmentOptions: ['全部'],
      buildingOptions: ['全部'],
      dormitoryOptions: [],
      temp: {
        studentId: undefined,
        name: '',
        gender: undefined,
        department: '',
        enroll: undefined,
        birth: '',
        dormId: undefined,
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
    this.getDepartment()
  },
  methods: {
    handleUpdateDorm(buildingName) {
      var listQuery = {
        BuildingName: buildingName
      }
      fetchDormitoryList(listQuery).then(response => {
        this.dormOptions = response.data.items
      })
    },
    getDepartment() {
      this.listLoading = true
      fetchDepartment().then(response => {
        // console.log(response)
        for (var j = 0, len = response.data.result.total_count; j < len; j++) {
          this.departmentOptions.push(response.data.result.list[j].name)
        }
      })
    },
    getList() {
      this.listLoading = true
      fetchStudentList(this.listQuery).then(response => {
        console.log(response.data)
        this.list = response.data.result.list
        console.log(this.list)
        this.total = response.data.result.total_count

        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    },
    getBuilding() {
      fetchBuildingList().then(response => {
        for (var j = 0, len = response.data.result.total_count; j < len; j++) {
          this.buildingOptions.push(response.data.result.list[j].name)
        }
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
          createStudent(this.temp).then(() => {
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
          updateStudent(tempData).then(() => {
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
      deleteStudent(row.id).then(response => {
        this.$notify({
          title: '成功',
          message: '删除成功',
          type: 'success',
          duration: 2000
        })
        const index = this.list.indexOf(row)
        this.list.splice(index, 1)
      })
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
