<template>
  <div>
    <div class="header">已发货订单</div>
    <div class="body">
      <el-table :data="tableData" style="width: 100%" class="table" border>
        <el-table-column prop="OrderID" label="订单编号" width="80" align="center">
        </el-table-column>
        <el-table-column prop="VendorName" label="店铺名" width="120" align="center">
        </el-table-column>
        <el-table-column prop="VendorAddress" label="取餐地址" width="200" align="center">
        </el-table-column>
        <el-table-column
          prop="ConsigneeName"
          label="顾客用户名"
          width="100"
          align="center"
        >
        </el-table-column>
        <el-table-column
          prop="ConsigneeAddress"
          label="送餐地址"
          width="200"
          align="center"
        >
        </el-table-column>
        <el-table-column prop="Price" label="订单价格" width="80" align="center">
        </el-table-column>
        <el-table-column prop="OrderTime" label="下单时间" width="200" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.OrderTime }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="Time" label="送达时间" width="200" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.Time ? scope.row.Time : "配送中" }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template slot-scope="scope">
            <el-button
              @click="markAsDelivered(scope.row.OrderID)"
              type="primary"
              size="mini"
              >送达</el-button
            >
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
        .get("/api/orders/sending", {
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
    markAsDelivered(order_id) {
      const token = localStorage.getItem("token");
      this.$axios
        .put(
          "/api/user/deliver",
          { orderId: order_id },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        )
        .then((res) => {
          if (res.data.status == 200) {
            this.$message.success("订单已标记为送达");
            this.getdata(); // 重新获取数据
          } else {
            this.$message.error("标记送达失败");
          }
        })
        .catch((error) => {
          console.error("Error marking order as delivered:", error);
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
