<template>
  <div>
    <div class="header">未发货订单</div>
    <div class="body">
      <el-table :data="tableData" style="width: 100%" class="table" border>
        <el-table-column prop="order_id" label="订单编号" width="80" align="center">
        </el-table-column>
        <el-table-column prop="shop_name" label="店铺名" width="120" align="center">
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
        <el-table-column prop="deliver_time" label="送达时间" width="200" align="center">
          <template>
            <span>未送达</span>
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
        .get("/api/user/orders/unsend", {
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
    deleteOrder(order_id) {
      const token = localStorage.getItem("token");
      this.$axios
        .delete(`/api/user/order/${order_id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        .then((res) => {
          if (res.data.status == 200) {
            this.$message.success("订单删除成功");
            this.getdata(); // 重新获取数据
          } else {
            this.$message.error("订单删除失败");
          }
        })
        .catch((error) => {
          console.error("Error deleting order:", error);
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
