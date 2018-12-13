<template>
  <div class="app-container">
    <div class="filter-container">
      <el-row type="flex" justify="space-between">
        <div>
          <el-input :placeholder="$t('dormitory.dormNum')" v-model="listQuery.DormNum" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter"/>
          <el-input :placeholder="$t('dormitory.buildingName')" v-model="listQuery.BuildingName" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter"/>
          <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">{{ $t('dormitory.search') }}</el-button>
        </div>
        <div>
          <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-edit" @click="handleCreate">{{ $t('dormitory.add') }}</el-button>
          <el-button v-waves :loading="downloadLoading" class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">{{ $t('dormitory.export') }}</el-button>
        </div>
      </el-row>
    </div>

    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;">
      <el-table-column :label="$t('dormitory.dormNum')" prop="id" sortable="custom" align="center" width="65">
        <template slot-scope="scope">
          <span>{{ scope.row.DormNum }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('dormitory.buildingName')" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.BuildingName }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('dormitory.waterMeterId')" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.WaterMeterId }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('dormitory.electricMeterId')" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.ElectricMeterId }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('dormitory.actions')" align="center" min-width="250" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button type="primary" align="center" size="mini" @click="handleFetchStu(scope.row.DormNum)">{{ $t('dormitory.livingstu') }}</el-button>
          <el-button type="primary" align="center" size="mini" @click="handleUpdate(scope.row)">{{ $t('dormitory.edit') }}</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row,'deleted')">{{ $t('dormitory.delete') }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item :label="$t('dormitory.dormNum')" prop="DormNum">
          <el-input v-model="temp.DormNum"/>
        </el-form-item>
        <el-form-item :label="$t('dormitory.buildingName')" prop="BuildingName">
          <el-input v-model="temp.BuildingName"/>
        </el-form-item>
        <el-form-item :label="$t('dormitory.electricMeterId')" prop="ElectricMeterId">
          <el-input v-model="temp.ElectricMeterId"/>
        </el-form-item>
        <el-form-item :label="$t('dormitory.waterMeterId')" prop="WaterMeterId">
          <el-input v-model="temp.WaterMeterId"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">{{ $t('table.cancel') }}</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">{{ $t('table.confirm') }}</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogStuVisible" :title="$t('dormitory.livingstu')">
      <el-table :data="stuData" border fit highlight-current-row style="width: 100%">
        <el-table-column :label="$t('dormitory.name')" prop="Name" />
        <el-table-column :label="$t('dormitory.studentid')" prop="Studentid" />
      </el-table>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogStuVisible = false">{{ $t('dormitory.confirm') }}</el-button>
      </span>
    </el-dialog>

  </div>
</template>

<script>
import { fetchList, createDormitory, updateDormitory } from '@/api/dormitory'
import { fetchList as fetchStudentList } from '@/api/student'
import waves from '@/directive/waves' // Waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // Secondary package based on el-pagination

export default {
  name: 'Dormitory',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        DormNum: undefined,
        BuildingName: undefined
      },
      temp: {
        DormNum: undefined,
        BuildingName: undefined,
        ElectricMeterId: undefined,
        WaterMeterId: undefined
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '修改',
        create: '创建'
      },
      dialogStuVisible: false,
      stuData: [],
      rules: {
        DormNum: [{ required: true, message: 'dormitory number is required', trigger: 'change' }],
        BuildingName: [{ required: true, message: 'building name is required', trigger: 'change' }],
        ElectricMeterId: [{ required: true, message: 'electric meter id is required', trigger: 'change' }],
        WaterMeterId: [{ required: true, message: 'water meter id is required', trigger: 'change' }]
      },
      downloadLoading: false
    }
  },
  created() {
    this.getList()
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
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    resetTemp() {
      this.temp = {
        DormNum: undefined,
        BuildingName: undefined,
        ElectricMeterId: undefined,
        WaterMeterId: undefined
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
          // this.temp.DormNum = parseInt(Math.random() * 100) + 1024 // mock a id
          // this.temp.author = 'vue-element-admin'
          createDormitory(this.temp).then(() => {
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
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          updateDormitory(tempData).then(() => {
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
    handleFetchStu(dormNum) {
      const query = {
        page: 1,
        limit: 20,
        department: '全部',
        status: '全部',
        name: undefined,
        studentId: undefined,
        dormId: dormNum,
        buildingName: '全部'
      }
      fetchStudentList(query).then(response => {
        console.log(response.data)
        this.stuData = response.data.stuData
        this.dialogStuVisible = true
      })
    },
    handleDownload() {
      this.downloadLoading = true
      import('@/vendor/Export2Excel').then(excel => {
        const tHeader = ['timestamp', 'title', 'type', 'importance', 'status']
        const filterVal = ['timestamp', 'title', 'type', 'importance', 'status']
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
