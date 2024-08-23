/*
 * This file is auto-generated. Modifications will be lost.
 *
 * See https://android.googlesource.com/platform/bionic/+/master/libc/kernel/
 * for more information.
 */
#ifndef _UAPI_RDMA_NETLINK_H
#define _UAPI_RDMA_NETLINK_H
#include <linux/types.h>
enum {
  RDMA_NL_IWCM = 2,
  RDMA_NL_RSVD,
  RDMA_NL_LS,
  RDMA_NL_NLDEV,
  RDMA_NL_NUM_CLIENTS
};
enum {
  RDMA_NL_GROUP_IWPM = 2,
  RDMA_NL_GROUP_LS,
  RDMA_NL_NUM_GROUPS
};
#define RDMA_NL_GET_CLIENT(type) ((type & (((1 << 6) - 1) << 10)) >> 10)
#define RDMA_NL_GET_OP(type) (type & ((1 << 10) - 1))
#define RDMA_NL_GET_TYPE(client,op) ((client << 10) + op)
#define IWPM_UABI_VERSION_MIN 3
#define IWPM_UABI_VERSION 4
enum {
  IWPM_FLAGS_NO_PORT_MAP = (1 << 0),
};
enum {
  RDMA_NL_IWPM_REG_PID = 0,
  RDMA_NL_IWPM_ADD_MAPPING,
  RDMA_NL_IWPM_QUERY_MAPPING,
  RDMA_NL_IWPM_REMOVE_MAPPING,
  RDMA_NL_IWPM_REMOTE_INFO,
  RDMA_NL_IWPM_HANDLE_ERR,
  RDMA_NL_IWPM_MAPINFO,
  RDMA_NL_IWPM_MAPINFO_NUM,
  RDMA_NL_IWPM_HELLO,
  RDMA_NL_IWPM_NUM_OPS
};
enum {
  IWPM_NLA_REG_PID_UNSPEC = 0,
  IWPM_NLA_REG_PID_SEQ,
  IWPM_NLA_REG_IF_NAME,
  IWPM_NLA_REG_IBDEV_NAME,
  IWPM_NLA_REG_ULIB_NAME,
  IWPM_NLA_REG_PID_MAX
};
enum {
  IWPM_NLA_RREG_PID_UNSPEC = 0,
  IWPM_NLA_RREG_PID_SEQ,
  IWPM_NLA_RREG_IBDEV_NAME,
  IWPM_NLA_RREG_ULIB_NAME,
  IWPM_NLA_RREG_ULIB_VER,
  IWPM_NLA_RREG_PID_ERR,
  IWPM_NLA_RREG_PID_MAX
};
enum {
  IWPM_NLA_MANAGE_MAPPING_UNSPEC = 0,
  IWPM_NLA_MANAGE_MAPPING_SEQ,
  IWPM_NLA_MANAGE_ADDR,
  IWPM_NLA_MANAGE_FLAGS,
  IWPM_NLA_MANAGE_MAPPING_MAX
};
enum {
  IWPM_NLA_RMANAGE_MAPPING_UNSPEC = 0,
  IWPM_NLA_RMANAGE_MAPPING_SEQ,
  IWPM_NLA_RMANAGE_ADDR,
  IWPM_NLA_RMANAGE_MAPPED_LOC_ADDR,
  IWPM_NLA_MANAGE_MAPPED_LOC_ADDR = IWPM_NLA_RMANAGE_MAPPED_LOC_ADDR,
  IWPM_NLA_RMANAGE_MAPPING_ERR,
  IWPM_NLA_RMANAGE_MAPPING_MAX
};
#define IWPM_NLA_MAPINFO_SEND_MAX 3
#define IWPM_NLA_REMOVE_MAPPING_MAX 3
enum {
  IWPM_NLA_QUERY_MAPPING_UNSPEC = 0,
  IWPM_NLA_QUERY_MAPPING_SEQ,
  IWPM_NLA_QUERY_LOCAL_ADDR,
  IWPM_NLA_QUERY_REMOTE_ADDR,
  IWPM_NLA_QUERY_FLAGS,
  IWPM_NLA_QUERY_MAPPING_MAX,
};
enum {
  IWPM_NLA_RQUERY_MAPPING_UNSPEC = 0,
  IWPM_NLA_RQUERY_MAPPING_SEQ,
  IWPM_NLA_RQUERY_LOCAL_ADDR,
  IWPM_NLA_RQUERY_REMOTE_ADDR,
  IWPM_NLA_RQUERY_MAPPED_LOC_ADDR,
  IWPM_NLA_RQUERY_MAPPED_REM_ADDR,
  IWPM_NLA_RQUERY_MAPPING_ERR,
  IWPM_NLA_RQUERY_MAPPING_MAX
};
enum {
  IWPM_NLA_MAPINFO_REQ_UNSPEC = 0,
  IWPM_NLA_MAPINFO_ULIB_NAME,
  IWPM_NLA_MAPINFO_ULIB_VER,
  IWPM_NLA_MAPINFO_REQ_MAX
};
enum {
  IWPM_NLA_MAPINFO_UNSPEC = 0,
  IWPM_NLA_MAPINFO_LOCAL_ADDR,
  IWPM_NLA_MAPINFO_MAPPED_ADDR,
  IWPM_NLA_MAPINFO_FLAGS,
  IWPM_NLA_MAPINFO_MAX
};
enum {
  IWPM_NLA_MAPINFO_NUM_UNSPEC = 0,
  IWPM_NLA_MAPINFO_SEQ,
  IWPM_NLA_MAPINFO_SEND_NUM,
  IWPM_NLA_MAPINFO_ACK_NUM,
  IWPM_NLA_MAPINFO_NUM_MAX
};
enum {
  IWPM_NLA_ERR_UNSPEC = 0,
  IWPM_NLA_ERR_SEQ,
  IWPM_NLA_ERR_CODE,
  IWPM_NLA_ERR_MAX
};
enum {
  IWPM_NLA_HELLO_UNSPEC = 0,
  IWPM_NLA_HELLO_ABI_VERSION,
  IWPM_NLA_HELLO_MAX
};
enum {
  RDMA_NODE_IB_CA = 1,
  RDMA_NODE_IB_SWITCH,
  RDMA_NODE_IB_ROUTER,
  RDMA_NODE_RNIC,
  RDMA_NODE_USNIC,
  RDMA_NODE_USNIC_UDP,
  RDMA_NODE_UNSPECIFIED,
};
enum {
  RDMA_NL_LS_OP_RESOLVE = 0,
  RDMA_NL_LS_OP_SET_TIMEOUT,
  RDMA_NL_LS_OP_IP_RESOLVE,
  RDMA_NL_LS_NUM_OPS
};
#define RDMA_NL_LS_F_ERR 0x0100
enum {
  LS_RESOLVE_PATH_USE_ALL = 0,
  LS_RESOLVE_PATH_USE_UNIDIRECTIONAL,
  LS_RESOLVE_PATH_USE_GMP,
  LS_RESOLVE_PATH_USE_MAX
};
#define LS_DEVICE_NAME_MAX 64
struct rdma_ls_resolve_header {
  __u8 device_name[LS_DEVICE_NAME_MAX];
  __u8 port_num;
  __u8 path_use;
};
struct rdma_ls_ip_resolve_header {
  __u32 ifindex;
};
#define RDMA_NLA_F_MANDATORY (1 << 13)
#define RDMA_NLA_TYPE_MASK (~(NLA_F_NESTED | NLA_F_NET_BYTEORDER | RDMA_NLA_F_MANDATORY))
enum {
  LS_NLA_TYPE_UNSPEC = 0,
  LS_NLA_TYPE_PATH_RECORD,
  LS_NLA_TYPE_TIMEOUT,
  LS_NLA_TYPE_SERVICE_ID,
  LS_NLA_TYPE_DGID,
  LS_NLA_TYPE_SGID,
  LS_NLA_TYPE_TCLASS,
  LS_NLA_TYPE_PKEY,
  LS_NLA_TYPE_QOS_CLASS,
  LS_NLA_TYPE_IPV4,
  LS_NLA_TYPE_IPV6,
  LS_NLA_TYPE_MAX
};
struct rdma_nla_ls_gid {
  __u8 gid[16];
};
enum rdma_nldev_command {
  RDMA_NLDEV_CMD_UNSPEC,
  RDMA_NLDEV_CMD_GET,
  RDMA_NLDEV_CMD_SET,
  RDMA_NLDEV_CMD_NEWLINK,
  RDMA_NLDEV_CMD_DELLINK,
  RDMA_NLDEV_CMD_PORT_GET,
  RDMA_NLDEV_CMD_SYS_GET,
  RDMA_NLDEV_CMD_SYS_SET,
  RDMA_NLDEV_CMD_RES_GET = 9,
  RDMA_NLDEV_CMD_RES_QP_GET,
  RDMA_NLDEV_CMD_RES_CM_ID_GET,
  RDMA_NLDEV_CMD_RES_CQ_GET,
  RDMA_NLDEV_CMD_RES_MR_GET,
  RDMA_NLDEV_CMD_RES_PD_GET,
  RDMA_NLDEV_CMD_GET_CHARDEV,
  RDMA_NLDEV_CMD_STAT_SET,
  RDMA_NLDEV_CMD_STAT_GET,
  RDMA_NLDEV_CMD_STAT_DEL,
  RDMA_NLDEV_CMD_RES_QP_GET_RAW,
  RDMA_NLDEV_CMD_RES_CQ_GET_RAW,
  RDMA_NLDEV_CMD_RES_MR_GET_RAW,
  RDMA_NLDEV_CMD_RES_CTX_GET,
  RDMA_NLDEV_CMD_RES_SRQ_GET,
  RDMA_NLDEV_CMD_STAT_GET_STATUS,
  RDMA_NLDEV_CMD_RES_SRQ_GET_RAW,
  RDMA_NLDEV_NUM_OPS
};
enum rdma_nldev_print_type {
  RDMA_NLDEV_PRINT_TYPE_UNSPEC,
  RDMA_NLDEV_PRINT_TYPE_HEX,
};
enum rdma_nldev_attr {
  RDMA_NLDEV_ATTR_UNSPEC,
  RDMA_NLDEV_ATTR_PAD = RDMA_NLDEV_ATTR_UNSPEC,
  RDMA_NLDEV_ATTR_DEV_INDEX,
  RDMA_NLDEV_ATTR_DEV_NAME,
  RDMA_NLDEV_ATTR_PORT_INDEX,
  RDMA_NLDEV_ATTR_CAP_FLAGS,
  RDMA_NLDEV_ATTR_FW_VERSION,
  RDMA_NLDEV_ATTR_NODE_GUID,
  RDMA_NLDEV_ATTR_SYS_IMAGE_GUID,
  RDMA_NLDEV_ATTR_SUBNET_PREFIX,
  RDMA_NLDEV_ATTR_LID,
  RDMA_NLDEV_ATTR_SM_LID,
  RDMA_NLDEV_ATTR_LMC,
  RDMA_NLDEV_ATTR_PORT_STATE,
  RDMA_NLDEV_ATTR_PORT_PHYS_STATE,
  RDMA_NLDEV_ATTR_DEV_NODE_TYPE,
  RDMA_NLDEV_ATTR_RES_SUMMARY,
  RDMA_NLDEV_ATTR_RES_SUMMARY_ENTRY,
  RDMA_NLDEV_ATTR_RES_SUMMARY_ENTRY_NAME,
  RDMA_NLDEV_ATTR_RES_SUMMARY_ENTRY_CURR,
  RDMA_NLDEV_ATTR_RES_QP,
  RDMA_NLDEV_ATTR_RES_QP_ENTRY,
  RDMA_NLDEV_ATTR_RES_LQPN,
  RDMA_NLDEV_ATTR_RES_RQPN,
  RDMA_NLDEV_ATTR_RES_RQ_PSN,
  RDMA_NLDEV_ATTR_RES_SQ_PSN,
  RDMA_NLDEV_ATTR_RES_PATH_MIG_STATE,
  RDMA_NLDEV_ATTR_RES_TYPE,
  RDMA_NLDEV_ATTR_RES_STATE,
  RDMA_NLDEV_ATTR_RES_PID,
  RDMA_NLDEV_ATTR_RES_KERN_NAME,
  RDMA_NLDEV_ATTR_RES_CM_ID,
  RDMA_NLDEV_ATTR_RES_CM_ID_ENTRY,
  RDMA_NLDEV_ATTR_RES_PS,
  RDMA_NLDEV_ATTR_RES_SRC_ADDR,
  RDMA_NLDEV_ATTR_RES_DST_ADDR,
  RDMA_NLDEV_ATTR_RES_CQ,
  RDMA_NLDEV_ATTR_RES_CQ_ENTRY,
  RDMA_NLDEV_ATTR_RES_CQE,
  RDMA_NLDEV_ATTR_RES_USECNT,
  RDMA_NLDEV_ATTR_RES_POLL_CTX,
  RDMA_NLDEV_ATTR_RES_MR,
  RDMA_NLDEV_ATTR_RES_MR_ENTRY,
  RDMA_NLDEV_ATTR_RES_RKEY,
  RDMA_NLDEV_ATTR_RES_LKEY,
  RDMA_NLDEV_ATTR_RES_IOVA,
  RDMA_NLDEV_ATTR_RES_MRLEN,
  RDMA_NLDEV_ATTR_RES_PD,
  RDMA_NLDEV_ATTR_RES_PD_ENTRY,
  RDMA_NLDEV_ATTR_RES_LOCAL_DMA_LKEY,
  RDMA_NLDEV_ATTR_RES_UNSAFE_GLOBAL_RKEY,
  RDMA_NLDEV_ATTR_NDEV_INDEX,
  RDMA_NLDEV_ATTR_NDEV_NAME,
  RDMA_NLDEV_ATTR_DRIVER,
  RDMA_NLDEV_ATTR_DRIVER_ENTRY,
  RDMA_NLDEV_ATTR_DRIVER_STRING,
  RDMA_NLDEV_ATTR_DRIVER_PRINT_TYPE,
  RDMA_NLDEV_ATTR_DRIVER_S32,
  RDMA_NLDEV_ATTR_DRIVER_U32,
  RDMA_NLDEV_ATTR_DRIVER_S64,
  RDMA_NLDEV_ATTR_DRIVER_U64,
  RDMA_NLDEV_ATTR_RES_PDN,
  RDMA_NLDEV_ATTR_RES_CQN,
  RDMA_NLDEV_ATTR_RES_MRN,
  RDMA_NLDEV_ATTR_RES_CM_IDN,
  RDMA_NLDEV_ATTR_RES_CTXN,
  RDMA_NLDEV_ATTR_LINK_TYPE,
  RDMA_NLDEV_SYS_ATTR_NETNS_MODE,
  RDMA_NLDEV_ATTR_DEV_PROTOCOL,
  RDMA_NLDEV_NET_NS_FD,
  RDMA_NLDEV_ATTR_CHARDEV_TYPE,
  RDMA_NLDEV_ATTR_CHARDEV_NAME,
  RDMA_NLDEV_ATTR_CHARDEV_ABI,
  RDMA_NLDEV_ATTR_CHARDEV,
  RDMA_NLDEV_ATTR_UVERBS_DRIVER_ID,
  RDMA_NLDEV_ATTR_STAT_MODE,
  RDMA_NLDEV_ATTR_STAT_RES,
  RDMA_NLDEV_ATTR_STAT_AUTO_MODE_MASK,
  RDMA_NLDEV_ATTR_STAT_COUNTER,
  RDMA_NLDEV_ATTR_STAT_COUNTER_ENTRY,
  RDMA_NLDEV_ATTR_STAT_COUNTER_ID,
  RDMA_NLDEV_ATTR_STAT_HWCOUNTERS,
  RDMA_NLDEV_ATTR_STAT_HWCOUNTER_ENTRY,
  RDMA_NLDEV_ATTR_STAT_HWCOUNTER_ENTRY_NAME,
  RDMA_NLDEV_ATTR_STAT_HWCOUNTER_ENTRY_VALUE,
  RDMA_NLDEV_ATTR_DEV_DIM,
  RDMA_NLDEV_ATTR_RES_RAW,
  RDMA_NLDEV_ATTR_RES_CTX,
  RDMA_NLDEV_ATTR_RES_CTX_ENTRY,
  RDMA_NLDEV_ATTR_RES_SRQ,
  RDMA_NLDEV_ATTR_RES_SRQ_ENTRY,
  RDMA_NLDEV_ATTR_RES_SRQN,
  RDMA_NLDEV_ATTR_MIN_RANGE,
  RDMA_NLDEV_ATTR_MAX_RANGE,
  RDMA_NLDEV_SYS_ATTR_COPY_ON_FORK,
  RDMA_NLDEV_ATTR_STAT_HWCOUNTER_INDEX,
  RDMA_NLDEV_ATTR_STAT_HWCOUNTER_DYNAMIC,
  RDMA_NLDEV_SYS_ATTR_PRIVILEGED_QKEY_MODE,
  RDMA_NLDEV_ATTR_DRIVER_DETAILS,
  RDMA_NLDEV_ATTR_RES_SUBTYPE,
  RDMA_NLDEV_ATTR_MAX
};
enum rdma_nl_counter_mode {
  RDMA_COUNTER_MODE_NONE,
  RDMA_COUNTER_MODE_AUTO,
  RDMA_COUNTER_MODE_MANUAL,
  RDMA_COUNTER_MODE_MAX,
};
enum rdma_nl_counter_mask {
  RDMA_COUNTER_MASK_QP_TYPE = 1,
  RDMA_COUNTER_MASK_PID = 1 << 1,
};
#endif
