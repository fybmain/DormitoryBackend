<template>
  <div class="app-container">
    <div class="filter-container">
      <el-row type="flex" class="row-bg" justify="end">
        <el-col>
          <el-input :placeholder="$t('student.studentid')" v-model="listQuery.filter.card_id" style="width: 100px;" class="filter-item" @keyup.enter.native="handleFilter"/>
          <el-input :placeholder="$t('student.name')" v-model="listQuery.filter.real_name" style="width: 100px;" class="filter-item" @keyup.enter.native="handleFilter"/>
          <el-select v-model="listQuery.filter.department" :placeholder="$t('student.department')" clearable style="width: 170px" class="filter-item">
            <el-option v-for="item in departmentOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
          <el-select v-model="building" :placeholder="$t('student.buildingname')" clearable style="width: 100px" class="filter-item" @change="getDormitory">
            <el-option v-for="item in buildingOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
          <el-select v-model="listQuery.filter.dormitory" :placeholder="$t('student.dormid')" clearable style="width: 100px" class="filter-item">
            <el-option v-for="item in dormitoryOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
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
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="80px" style="width: 400px; margin-left:50px;">
        <el-form-item :label="$t('student.name')" prop="real_name">
          <el-input v-model="temp.real_name"/>
        </el-form-item>
        <el-form-item v-if="textMap[dialogStatus]=='创建'" label="密码" prop="password">
          <el-input v-model="temp.password"/>
        </el-form-item>
        <el-form-item :label="$t('student.studentid')" prop="card_id">
          <el-input v-model="temp.card_id"/>
        </el-form-item>
        <el-form-item :label="$t('student.gender')" prop="gender">
          <el-input v-model="temp.gender"/>
        </el-form-item>
        <el-form-item :label="$t('student.department')" prop="department">
          <el-select v-model="temp.department.id" class="filter-item" placeholder="Please select">
            <el-option v-for="item in departmentOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('student.birth')" prop="birth_date">
          <el-date-picker v-model="temp.birth_date" type="datetime" placeholder="Please pick a date"/>
        </el-form-item>
        <el-form-item :label="$t('student.enroll')" prop="enroll_date">
          <el-date-picker v-model="temp.enroll_date" type="datetime" placeholder="Please pick a date"/>
        </el-form-item>
        <el-form-item :label="$t('student.buildingname')" prop="dormitory.building">
          <el-select v-model="temp.dormitory.building.id" class="filter-item" placeholder="Please select" @change="handleUpdateDorm(temp.dormitory.building.id)" >
            <el-option v-for="item in buildingOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('student.dormid')" prop="dormitory">
          <el-select v-model="temp.dormitory.id" class="filter-item" placeholder="Please select">
            <el-option v-for="item in dormitoryOptions" :key="item.id" :label="item.name" :value="item.id"/>
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
import { fetchList as fetchStudentList, createStudent, updateStudent } from '@/api/student'
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
          department: undefined,
          real_name: undefined,
          card_id: undefined,
          dormitory: undefined
        }
      },
      building: undefined,
      departmentOptions: [{ id: 0, name: '全部' }],
      buildingOptions: [{ id: 0, name: '全部' }],
      dormitoryOptions: [],
      temp: {
        card_id: undefined,
        real_name: undefined,
        password: undefined,
        gender: undefined,
        department: { id: undefined, name: undefined },
        enroll_date: undefined,
        birth_date: undefined,
        dormitory: { building: { id: undefined, name: undefined }, id: undefined, number: undefined }
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '修改',
        create: '创建'
      },
      rules: {
        real_name: [{ required: true, message: 'name is required', trigger: 'change' }],
        card_id: [{ required: true, message: 'student id is required', trigger: 'change' }],
        gender: [{ required: true, message: 'name is required', trigger: 'change' }],
        department: [{ required: true, message: 'department is required', trigger: 'change' }],
        birth_date: [{ required: true, message: 'birth is required', trigger: 'change' }],
        enroll_date: [{ required: true, message: 'enroll is required', trigger: 'change' }],
        dormitory: [{ required: true, message: 'dorm id is required', trigger: 'change' }]
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
    handleUpdateDorm(id) {
      this.dormitoryOptions = []
      this.temp.dormitory.id = undefined
      this.temp.dormitory.name = undefined
      if (id === 0) { return }
      fetchDormitoryList({ page: 1, limit: 20, filter: { building: id }}).then(response => {
        for (var j = 0, len = response.data.result.total_count; j < len; j++) {
          this.dormitoryOptions.push({ id: response.data.result.list[j].id, name: response.data.result.list[j].number })
        }
      })
    },
    getDormitory() {
      this.listLoading = true
      this.dormitoryOptions = []
      this.listQuery.filter.dormitory = undefined
      if (this.building === '' || this.building === undefined || this.building === 0) {
        this.building = undefined
        this.listLoading = false
      } else {
        fetchDormitoryList({ page: 1, limit: 20, filter: { building: this.building }}).then((response) => {
          for (var j = 0, len = response.data.result.total_count; j < len; j++) {
            this.dormitoryOptions.push({ id: response.data.result.list[j].id, name: response.data.result.list[j].number })
          }
          this.listLoading = false
        })
      }
    },
    getDepartment() {
      this.listLoading = true
      fetchDepartment().then(response => {
        for (var j = 0, len = response.data.result.total_count; j < len; j++) {
          this.departmentOptions.push({ id: response.data.result.list[j].id, name: response.data.result.list[j].name })
        }
      })
    },
    getList() {
      this.listLoading = true
      fetchStudentList(this.listQuery).then(response => {
        this.list = response.data.result.list
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
          this.buildingOptions.push({ id: response.data.result.list[j].id, name: response.data.result.list[j].name })
        }
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      if (this.listQuery.filter.department === '') { this.listQuery.filter.department = undefined }
      this.getList()
    },
    resetTemp() {
      this.temp = {
        card_id: undefined,
        password: undefined,
        real_name: undefined,
        gender: undefined,
        department: { id: undefined, name: undefined },
        enroll_date: undefined,
        birth_date: undefined,
        dormitory: { building: { id: undefined, name: undefined }, id: undefined, number: undefined }
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
          const post = {
            obj: {
              password: this.temp.password,
              card_id: this.temp.card_id,
              real_name: this.temp.real_name,
              gender: this.temp.gender,
              graduate_date: null,
              birth_date: parseTime(this.temp.birth_date, '{y}-{m}-{d}'),
              enroll_date: parseTime(this.temp.enroll_date, '{y}-{m}-{d}'),
              department: this.temp.department.id,
              leaved: false,
              dormitory: this.temp.dormitory.id
            }
          }
          console.log(post)
          createStudent(post).then((res) => {
            for (let i = 0; i < this.departmentOptions.length; i++) {
              if (this.temp.department.id === this.departmentOptions[i].id) {
                this.temp.department.name = this.departmentOptions[i].name
              }
            }
            for (let i = 0; i < this.dormitoryOptions.length; i++) {
              if (this.temp.dormitory.id === this.dormitoryOptions[i].id) {
                this.temp.dormitory.name = this.dormitoryOptions[i].name
              }
            }
            for (let i = 0; i < this.buildingOptions.length; i++) {
              if (this.temp.dormitory.building.id === this.buildingOptions[i].id) {
                this.temp.dormitory.building.name = this.buildingOptions[i].name
              }
            }
            this.temp.id = res.data.result.id
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
      this.dialogStatus = 'update'
      this.temp.enroll_date = parseTime(this.temp.enroll_date, '{y}-{m}-{d}')
      this.temp.birth_date = parseTime(this.temp.birth_date, '{y}-{m}-{d}')
      fetchDormitoryList({ page: 1, limit: 20, filter: { building: this.temp.dormitory.building.id }}).then(response => {
        for (var j = 0, len = response.data.result.total_count; j < len; j++) {
          this.dormitoryOptions.push({ id: response.data.result.list[j].id, name: response.data.result.list[j].number })
        }
      })
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      console.log(this.temp)
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          const post = {
            filter: {
              id: tempData.id
            },
            obj: {
              card_id: tempData.card_id,
              real_name: tempData.real_name,
              gender: tempData.gender,
              birth_date: tempData.birth_date,
              enroll_date: tempData.enroll_date,
              department: tempData.department.id,
              dormitory: tempData.dormitory.id
            }
          }
          updateStudent(post).then((res) => {
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
