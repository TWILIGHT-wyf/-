<template>
  <div>
    <div class="header">已发货订单</div>
    <div class="body">
      <el-table :data="tableData" style="width: 100%" class="table" border>
        <el-table-column prop="order_id" label="订单编号" width="80" align="center">
        </el-table-column>
        <el-table-column prop="dish_name" label="菜品名" width="120" align="center">
        </el-table-column>
        <el-table-column prop="rider_name" label="骑手名" width="120" align="center">
        </el-table-column>
        <el-table-column prop="cons_name" label="顾客用户名" width="100" align="center">
        </el-table-column>
        <el-table-column prop="price" label="订单价格" width="80" align="center">
        </el-table-column>
        <el-table-column prop="create_time" label="下单时间" width="200" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.create_time }}</span>
          </template>
        </el-table-column>
        <el-table-column label="送达时间" width="200" align="center">
          <template>
            <span>配送中</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
export default {
  created() {
    this.getdata();
  },
  data() {
    return {
      tableData: [],
    };
  },
  methods: {
    getdata() {
      const token = localStorage.getItem("token");
      this.$axios
        .get("/api/user/sending", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then((res) => {
          console.log(res.data);
          if (res.data.status == 200) {
            this.tableData = res.data.tabledata;
          }
        })
        .catch((error) => {
          console.error("Error fetching data:", error);
        });
    },
  },
};
</script>

<style scoped>
.header {
  width: 100%;
  height: 10%;
  text-align: center;
  line-height: 64px;
  font-size: 20px;
  font-weight: 800;
  border-bottom: 1px solid #e3e3e3;
}

.body {
  width: 76%;
  margin: auto;
  margin-top: 30px;
}
</style>
