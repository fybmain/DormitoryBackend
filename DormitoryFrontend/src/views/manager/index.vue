<template>
  <div class="app-container">
    <div class="filter-container">
      <el-row type="flex" justify="space-between">
        <div>
          <el-input v-model="listQuery.filter.real_name" placeholder="姓名" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter"/>
          <el-select v-model="listQuery.filter.building" placeholder="所属楼栋" clearable style="width: 90px" class="filter-item">
            <el-option v-for="item in buildingOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
          <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">搜索</el-button>
        </div>
        <div>
          <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-edit" @click="handleCreate">添加</el-button>
          <el-button v-waves :loading="downloadLoading" class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">导出</el-button>
        </div>
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
      <el-table-column label="id" prop="id" sortable="custom" align="center" width="65">
        <template slot-scope="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="姓名" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.real_name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="所属楼栋" width="110px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.building.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="入职日期" width="110px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.enter_date | parseTime('{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" min-width="230" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button type="primary" size="mini" @click="handleUpdate(scope.row)">修改</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="temp.real_name"/>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="temp.password"/>
        </el-form-item>
        <el-form-item label="所属楼栋" prop="building">
          <el-select v-model="temp.building.id" placeholder="所属楼栋" clearable style="width: 100px" class="filter-item" >
            <el-option v-for="item in buildingOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="入职日期" prop="enter_date">
          <el-date-picker v-model="temp.enter_date" type="datetime" placeholder="Please pick a date"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">{{ $t('table.cancel') }}</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">{{ $t('table.confirm') }}</el-button>
      </div>
    </el-dialog>

  </div>
</template>

<script>
import { fetchList, createManager, updateManager } from '@/api/manager'
import { fetchAll as fetchBuildingList } from '@/api/building'
import waves from '@/directive/waves' // Waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // Secondary package based on el-pagination

export default {
  name: 'Manger',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      tableKey: 0,
      list: null,
      total: 0,
      listLoading: true,
      buildingOptions: [{ id: 0, name: '全部' }],
      listQuery: {
        page: 1,
        limit: 20,
        filter: {
          real_name: undefined
        }
      },
      temp: {
        real_name: undefined,
        password: undefined,
        building: { id: undefined, name: undefined },
        leaved: false,
        enter_date: undefined,
        leave_date: undefined
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '修改',
        create: '创建'
      },
      rules: {
        building: [{ required: true, message: 'type is required', trigger: 'change' }],
        real_name: [{ type: 'string', required: true, message: 'timestamp is required', trigger: 'change' }],
        enter_date: [{ type: 'date', required: true, message: 'enter date is requires', trigger: 'change' }]
      },
      downloadLoading: false
    }
  },
  created() {
    this.getList()
    this.getBuilding()
  },
  methods: {
    getBuilding() {
      fetchBuildingList().then(response => {
        for (var j = 0, len = response.data.result.total_count; j < len; j++) {
          this.buildingOptions.push({ id: response.data.result.list[j].id, name: response.data.result.list[j].name })
        }
      })
    },
    getList() {
      this.listLoading = true
      fetchList(this.listQuery).then(response => {
        this.list = response.data.result.list
        this.total = response.data.result.total_count

        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      console.log(this.listQuery)
      if (this.listQuery.filter.real_name === '') this.listQuery.filter.real_name = undefined
      if (this.listQuery.filter.building === 0 || this.listQuery.filter.building === '') { this.listQuery.filter.building = undefined }
      this.getList()
    },
    resetTemp() {
      this.temp = {
        real_name: undefined,
        password: undefined,
        building: { id: undefined, name: undefined },
        leaved: false,
        enter_date: undefined,
        leave_date: undefined
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
          console.log(this.temp)
          const post = {
            obj: {
              real_name: this.temp.real_name,
              password: this.temp.password,
              enter_date: parseTime(this.temp.enter_date, '{y}-{m}-{d}'),
              leaved: false,
              leave_date: null,
              building: this.temp.building.id
            }
          }
          createManager(post).then((res) => {
            console.log(res)
            this.temp.id = res.data.result.id
            for (let i = 0; i < this.buildingOptions.length; i++) {
              if (this.temp.building.id === this.buildingOptions[i].id) {
                this.temp.building.name = this.buildingOptions[i].name
              }
            }
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
          updateManager(tempData).then(() => {
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
