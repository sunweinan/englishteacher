<template>
  <div>
    <h2>会员列表</h2>
    <p class="tip">可展开查看电话、级别、剩余时间、充值记录、推荐人数。</p>
    <el-table :data="members" row-key="phone" style="width: 100%">
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="detail">
            <p>电话：{{ row.phone }}</p>
            <p>会员级别：{{ row.level }} (剩余 {{ row.remaining }})</p>
            <p>充值记录：{{ row.recharges.join('，') }}</p>
            <p>推荐人数：{{ row.referrals }}</p>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="昵称" />
      <el-table-column prop="phone" label="手机号" />
      <el-table-column prop="level" label="等级" />
      <el-table-column prop="remaining" label="剩余时间" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
const members = [
  { name: 'Ava', phone: '138****8888', level: '年卡', remaining: '260天', recharges: ['¥30 年卡'], referrals: 6 },
  { name: 'Leo', phone: '139****5566', level: '月卡', remaining: '22天', recharges: ['¥10 月卡', '¥1 日卡'], referrals: 2 },
  { name: 'Nina', phone: '137****1020', level: '终身', remaining: '永久', recharges: ['¥40 终身'], referrals: 18 }
];
</script>

<style scoped>
.tip {
  color: #94a3b8;
  margin-bottom: 8px;
}

.detail {
  padding: 10px 14px;
  background: #f8fafc;
  border-radius: 8px;
}
</style>
