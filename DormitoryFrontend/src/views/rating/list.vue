<template>
  <div class="app-container">
    <div class="filter-container">
      <el-row type="flex" justify="space-between">
        <div>
          <el-select v-model="building" :placeholder="$t('dormitory.buildingName')" clearable style="width: 100px" class="filter-item" @change="getDormitory">
            <el-option v-for="item in buildingOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
          <el-select v-model="listQuery.filter.dormitory.id" :placeholder="$t('student.dormid')" clearable style="width: 100px" class="filter-item">
            <el-option v-for="item in dormitoryOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
          <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">{{ $t('table.search') }}</el-button>
        </div>
        <div>
          <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-edit" @click="handleCreate">{{ $t('table.add') }}</el-button>
          <el-button v-waves :loading="downloadLoading" class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">{{ $t('table.export') }}</el-button>
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
      <el-table-column label="id" align="center" width="100px">
        <template slot-scope="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="宿舍号" align="center" width="100px">
        <template slot-scope="scope">
          <span>{{ scope.row.dormitory.number }}</span>
        </template>
      </el-table-column>
      <el-table-column label="日期" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.date | parseTime('{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="评价" width="100px">
        <template slot-scope="scope">
          <svg-icon v-for="n in +scope.row.rating" :key="n" icon-class="star" class="meta-item__icon"/>
        </template>
      </el-table-column>
      <el-table-column :label="$t('table.actions')" align="center" min-width="230" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button type="primary" size="mini" @click="handleUpdate(scope.row)">修改</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item label="楼栋名">
          <el-select v-model="building" :placeholder="$t('dormitory.buildingName')" clearable style="width: 100px" class="filter-item" @change="getDormitory">
            <el-option v-for="item in buildingOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="宿舍号" prop="dormitory">
          <el-select v-model="temp.dormitory.id" :placeholder="$t('student.dormid')" clearable style="width: 100px" class="filter-item">
            <el-option v-for="item in dormitoryOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('table.date')" prop="date">
          <el-date-picker v-model="temp.date" type="datetime" placeholder="Please pick a date"/>
        </el-form-item>
        <el-form-item label="评价">
          <el-rate v-model="temp.rating" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" :max="5" style="margin-top:8px;"/>
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
import { fetchList, createRating, updateRating } from '@/api/rating'
import { fetchAll as fetchBuildingList } from '@/api/building'
import waves from '@/directive/waves' // Waves directive
import { fetchList as fetchDormitoryList } from '@/api/dormitory'
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // Secondary package based on el-pagination

export default {
  name: 'Rating',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      tableKey: 0,
      list: null,
      building: undefined,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        filter: {
          dormitory: {
            id: undefined
          }
        }
      },
      buildingOptions: [],
      dormitoryOptions: [],
      importanceOptions: [1, 2, 3, 4, 5],
      temp: {
        id: undefined,
        rating: 1,
        date: new Date(),
        dormitory: {
          id: undefined
        }
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '修改',
        create: '创建'
      },
      rules: {
        type: [{ required: true, message: 'type is required', trigger: 'change' }],
        timestamp: [{ type: 'date', required: true, message: 'timestamp is required', trigger: 'change' }],
        title: [{ required: true, message: 'title is required', trigger: 'blur' }]
      },
      downloadLoading: false
    }
  },
  created() {
    this.getList()
    this.getBuilding()
  },
  methods: {
    getDormitory() {
      this.dormitoryOptions = []
      this.listQuery.filter.dormitory.number = undefined
      if (this.building === '' || this.building === undefined) {
        this.building = undefined
      } else {
        fetchDormitoryList({ page: 1, limit: 20, filter: { id: this.building }}).then((response) => {
          for (var j = 0, len = response.data.result.total_count; j < len; j++) {
            this.dormitoryOptions.push({ id: response.data.result.list[j].id, name: response.data.result.list[j].number })
          }
        })
      }
    },
    getBuilding() {
      fetchBuildingList().then(response => {
        for (var j = 0, len = response.data.result.total_count; j < len; j++) {
          this.buildingOptions.push({ id: response.data.result.list[j].id, name: response.data.result.list[j].name })
        }
      })
    },
    getList() {
      this.listLoading = true
      fetchList(this.listQuery).then((response) => {
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
      if (this.listQuery.filter.dormitory.id === '') { this.listQuery.filter.dormitory.id = undefined }
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        rating: 1,
        date: new Date(),
        dormitory: {
          id: undefined
        }
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
    ShowBuildingName(id) {
      for (var i = 0; i < this.dormitoryOptions.length; i++) {
        if (id === this.dormitoryOptions[i].id) {
          return this.dormitoryOptions[i].name
        }
      }
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          console.log(this.temp)
          // const tempData = Object.assign({}, this.temp)
          const post = {
            obj: {
              date: parseTime(this.temp.date, '{y}-{m}-{d}'),
              rating: this.temp.rating,
              dormitory: this.temp.dormitory.id
            }
          }
          createRating(post).then((res) => {
            this.temp.id = res.data.result.id
            this.temp.dormitory.number = this.ShowBuildingName(this.temp.dormitory.id)
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
          // const tempData = Object.assign({}, this.temp)
          const post = {
            filter: {
              id: this.temp.dormitory.id
            },
            obj: {
              date: parseTime(this.temp.date, '{y}-{m}-{d}'),
              rating: this.temp.rating
            }
          }
          updateRating(post).then((res) => {
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
