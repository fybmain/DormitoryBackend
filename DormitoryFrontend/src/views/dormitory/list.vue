<template>
  <div class="app-container">
    <div class="filter-container">
      <el-row type="flex" justify="space-between">
        <div>
          <el-input :placeholder="$t('dormitory.dormNum')" v-model="listQuery.filter.number" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter"/>
          <el-select v-model="listQuery.filter.building" :placeholder="$t('dormitory.buildingName')" clearable style="width: 100px" class="filter-item" >
            <el-option v-for="item in buildingOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
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
          <span>{{ scope.row.number }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('dormitory.buildingName')" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.building.name }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('dormitory.waterMeterId')" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.water_meter }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('dormitory.electricMeterId')" width="150px" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.electricity_meter }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="$t('dormitory.actions')" align="center" min-width="250" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button type="primary" align="center" size="mini" @click="handleFetchStu(scope.row.id)">{{ $t('dormitory.livingstu') }}</el-button>
          <el-button type="primary" align="center" size="mini" @click="handleUpdate(scope.row)">{{ $t('dormitory.edit') }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item :label="$t('dormitory.dormNum')" prop="number">
          <el-input v-model="temp.number"/>
        </el-form-item>
        <el-form-item :label="$t('dormitory.buildingName')" prop="building">
          <el-select v-model="temp.building.id" :placeholder="$t('dormitory.buildingName')" clearable style="width: 100px" class="filter-item" >
            <el-option v-for="item in buildingOptions" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('dormitory.electricMeterId')" prop="electricity_meter">
          <el-input v-model.number="temp.electricity_meter"/>
        </el-form-item>
        <el-form-item :label="$t('dormitory.waterMeterId')" prop="water_meter">
          <el-input v-model.number="temp.water_meter"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">{{ $t('table.cancel') }}</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">{{ $t('table.confirm') }}</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogStuVisible" :title="$t('dormitory.livingstu')">
      <el-table :data="stuData" border fit highlight-current-row style="width: 100%">
        <el-table-column :label="$t('dormitory.name')" prop="real_name" />
        <el-table-column :label="$t('dormitory.studentid')" prop="card_id" />
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
import { fetchAll as fetchBuildingList } from '@/api/building'
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
        filter: {
          number: undefined,
          building: undefined
        }
      },
      temp: {
        number: undefined,
        building: { name: undefined, id: undefined },
        electricity_meter: undefined,
        water_meter: undefined
      },
      dialogFormVisible: false,
      dialogStatus: '',
      buildingOptions: [{ id: 0, name: '全部' }],
      textMap: {
        update: '修改',
        create: '创建'
      },
      dialogStuVisible: false,
      stuData: [],
      rules: {
        number: [{ required: true, message: 'dormitory number is required', trigger: 'change' }],
        building: [{ required: true, message: 'building name is required', trigger: 'change' }],
        electricity_meter: [{ type: 'integer', required: true, message: 'electricity meter id is required', trigger: 'change' }],
        water_meter: [{ type: 'integer', required: true, message: 'water meter id is required', trigger: 'change' }]
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
        console.log(this.buildingOptions)
      })
    },
    getList() {
      this.listLoading = true
      fetchList(this.listQuery).then(response => {
        console.log(response)
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
      console.log(this.listQuery.filter)
      if (this.listQuery.filter.building === 0 || this.listQuery.filter.building === '') { this.listQuery.filter.building = undefined }
      if (this.listQuery.filter.number === '') { this.listQuery.filter.number = undefined }
      this.getList()
    },
    resetTemp() {
      this.temp = {
        number: undefined,
        building: { id: undefined, name: undefined },
        electricity_meter: undefined,
        water_meter: undefined
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
      for (var i = 0; i < this.buildingOptions.length; i++) {
        if (id === this.buildingOptions[i].id) {
          return this.buildingOptions[i].name
        }
      }
    },
    createData() {
      console.log(this.temp)
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          createDormitory({ obj: { number: this.temp.number, building: this.temp.building.id, electricity_meter: this.temp.electricity_meter,
            water_meter: this.temp.water_meter }}).then((response) => {
            this.temp.building.name = this.ShowBuildingName(this.temp.building.id)
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
      this.temp.id = row.id
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
          updateDormitory({ obj: { number: tempData.number, building: tempData.building.id,
            electricity_meter: tempData.electricity_meter, water_meter: tempData.water_meter }, filter: { id: tempData.id }}).then((res) => {
            this.temp.building.name = this.ShowBuildingName(tempData.building.id)
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
    handleFetchStu(id) {
      const query = {
        page: 1,
        limit: 20,
        filter: {
          dormitory: id
        }
      }
      fetchStudentList(query).then(response => {
        this.stuData = response.data.result.list
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
